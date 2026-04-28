from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from models.assessment import AssessmentAttempt
from models.question import Question
from core.neo4j import get_driver
from collections import defaultdict

from google import genai
from google.genai import types
import os
import json

def process_assessment_submission(db: Session, submission: AssessmentSubmission):
    driver = get_driver()
    
    # Configurar Auditor
    client = genai.Client()

    option_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    detailed_results = []

    with driver.session() as session:
        for answer in submission.answers:
            result = session.run("""
                MATCH (q:Question {id: $id})
                OPTIONAL MATCH (q)-[:EVALUATES]->(s:Skill)
                RETURN q.answer as correct_answer, 
                       q.text as text,
                       collect(DISTINCT s.id) as skills,
                       q.difficulty as difficulty
                LIMIT 1
            """, id=answer.question_id).single()

            if result:
                user_letter = option_map.get(answer.selected_option_id)
                is_correct = result["correct_answer"] == user_letter
                
                detailed_results.append({
                    "question_id": answer.question_id,
                    "is_correct": is_correct,
                    "time_seconds": answer.time_seconds,
                    "difficulty": result["difficulty"],
                    "skills": result["skills"]
                })

        # --- Auditoria Pedagógica via IA ---
        audit_prompt = f"""
        Analise o padrão de respostas deste estudante no ENEM para detectar possíveis chutes (guesses).
        
        CRITÉRIOS CRÍTICOS:
        1. TEMPO EXTREMAMENTE CURTO (< 3s): Indica alta probabilidade de chute ou automação. Confidence deve ser < 0.2.
        2. TEMPO CURTO (< 10s) EM MÉDIAS/DIFÍCEIS: Provável chute. Confidence deve ser < 0.4.
        
        RESPOSTAS:
        {json.dumps(detailed_results)}
        
        Retorne um JSON:
        {{
          "audit": [
            {{
              "question_id": "string",
              "confidence_score": 0.0 a 1.0
            }}
          ]
        }}
        """
        try:
            audit_resp = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=audit_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            audit_data = json.loads(audit_resp.text)["audit"]
            confidence_map = {item["question_id"]: item["confidence_score"] for item in audit_data}
        except Exception as e:
            from core.logger import logger
            logger.error(f"Gemini audit failed, using conservative fallback: {str(e)}")
            # Usar heurística local para scores conservadores
            confidence_map = {}
            for res in detailed_results:
                time_spent = res.get("time_seconds", 30)
                difficulty = res.get("difficulty", "Médio")
                
                if time_spent < 5:
                    confidence_map[res["question_id"]] = 0.1
                elif time_spent < 10 and difficulty in ["Médio", "Difícil"]:
                    confidence_map[res["question_id"]] = 0.4
                else:
                    confidence_map[res["question_id"]] = 1.0

        # --- Processar Proficiências com Pesos ---
        scores = defaultdict(float)
        totals = defaultdict(int)

        from core.logger import logger
        logger.debug(f"Processing {len(detailed_results)} assessment results for audit.")

        for res in detailed_results:
            q_id = res["question_id"]
            confidence = confidence_map.get(q_id, 1.0)
            
            # GARANTIA: Penalidade absoluta por tempo (Previne o erro de 100% no Auto-Fill)
            is_penalty = False
            if res["time_seconds"] < 5: # Aumentado para 5s para ser mais rigoroso
                confidence = 0.1
                is_penalty = True
            elif res["time_seconds"] < 12 and res["difficulty"] in ["Médio", "Difícil"]:
                confidence = min(confidence, 0.4)
                is_penalty = True

            for item_id in res["skills"]:
                totals[item_id] += 1
                if res["is_correct"]:
                    # Se houver penalidade, o score é limitado a 0.2 mesmo que a IA diga o contrário
                    val = 1.0 * confidence
                    if is_penalty:
                        val = min(val, 0.2)
                    scores[item_id] += val

        proficiencies_data = []
        for item_id, total in totals.items():
            score = scores[item_id] / total if total > 0 else 0
            # Cap final de segurança: nada passa de 1.0 (obviamente) mas ajuda a debugar
            score = min(score, 1.0)
            proficiencies_data.append({"id": item_id, "score": float(score)})
            logger.debug(f"Skill {item_id} -> Final Score: {score}")
        
        enriched_proficiencies = []
        if proficiencies_data:
            # 1. Enriquecer dados para o snapshot da tentativa (somente desta prova)
            enriched_result = session.run("""
                UNWIND $profs AS p
                MATCH (s:Skill {id: p.id})
                OPTIONAL MATCH (s)-[:PART_OF]->(c:Competence)-[:BELONGS_TO]->(a:Area)
                RETURN s.id as id, 
                       s.description as description, 
                       p.score as score,
                       a.name as area,
                       labels(s)[0] as type
            """, profs=proficiencies_data)
            enriched_proficiencies = [dict(record) for record in enriched_result]

            # 2. Gravar novas proficiências e propagar (SEM DELETAR ANTIGAS - CUMULATIVO NO GRAFO)
            session.run("""
                MERGE (u:User {id: $user_id})
                WITH u
                UNWIND $proficiencies AS prof
                MATCH (target) WHERE target.id = prof.id
                MERGE (u)-[r:HAS_PROFICIENCY]->(target)
                SET r.score = prof.score, r.is_inferred = false
                
                // Propagação seletiva: só propaga se o score original for alto (> 0.6)
                WITH u, target, r
                WHERE r.score > 0.6
                MATCH (target)-[:PART_OF]->(c:Competence)<-[:PART_OF]-(related:Skill)
                WHERE NOT (u)-[:HAS_PROFICIENCY]->(related)
                MERGE (u)-[r2:HAS_PROFICIENCY]->(related)
                SET r2.score = r.score * 0.2, r2.is_inferred = true
                
                WITH u
                UNWIND $answered_ids AS q_id
                MATCH (q:Question {id: q_id})
                MERGE (u)-[:ANSWERED]->(q)
            """, user_id=submission.user_id, proficiencies=proficiencies_data, answered_ids=[a.question_id for a in submission.answers])

    # --- SQL Persistence: Record the Attempt with Snapshot ---
    new_attempt = AssessmentAttempt(
        user_id=submission.user_id,
        type=submission.type,
        proficiencies_snapshot=enriched_proficiencies
    )
    db.add(new_attempt)
    
    # Atualizar status do usuário se for um diagnóstico inicial/geral
    if submission.type in ["diagnostico", "inicial"]:
        from models.user import User
        db.query(User).filter(User.id == submission.user_id).update({"is_diagnostic_completed": True})
    
    db.commit()
    db.refresh(new_attempt)

    # Calcular se houve muitos chutes (opcional, para feedback na UI)
    low_confidence_count = sum(1 for c in confidence_map.values() if c < 0.5)
    has_cheated = low_confidence_count > (len(detailed_results) / 3)

    return {
        "status": "success", 
        "message": "Diagnóstico processado. Auditoria e propagação concluídas.",
        "attempt_id": new_attempt.id,
        "audit_summary": {
            "low_confidence_count": low_confidence_count,
            "has_warnings": has_cheated
        }
    }
