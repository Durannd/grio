from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from models.question import Question
from core.neo4j import get_driver
from collections import defaultdict

import google.generativeai as genai
import os
import json

def process_assessment_submission(db: Session, submission: AssessmentSubmission):
    driver = get_driver()
    
    # Configurar Auditor
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        generation_config={"response_mime_type": "application/json"}
    )

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
            audit_resp = model.generate_content(audit_prompt)
            audit_data = json.loads(audit_resp.text)["audit"]
            confidence_map = {item["question_id"]: item["confidence_score"] for item in audit_data}
        except:
            confidence_map = {res["question_id"]: 1.0 for res in detailed_results}

        # --- Processar Proficiências com Pesos ---
        scores = defaultdict(float)
        totals = defaultdict(int)

        for res in detailed_results:
            q_id = res["question_id"]
            confidence = confidence_map.get(q_id, 1.0)
            
            # GARANTIA: Penalidade absoluta por tempo (Previne o erro de 100% no Auto-Fill)
            if res["time_seconds"] < 3:
                confidence = 0.1
            elif res["time_seconds"] < 10 and res["difficulty"] in ["Médio", "Difícil"]:
                confidence = min(confidence, 0.4)

            for item_id in res["skills"]:
                totals[item_id] += 1
                if res["is_correct"]:
                    scores[item_id] += (1.0 * confidence)

        proficiencies_data = []
        for item_id, total in totals.items():
            score = scores[item_id] / total if total > 0 else 0
            proficiencies_data.append({"id": item_id, "score": score})
        
        if proficiencies_data:
            # 1. Limpar proficiências e análises antigas
            session.run("""
                MATCH (u:User {id: $user_id})
                OPTIONAL MATCH (u)-[r:HAS_PROFICIENCY]->()
                DELETE r
                SET u.latest_analysis = null
            """, user_id=submission.user_id)

            # 2. Gravar novas proficiências e propagar
            session.run("""
                MERGE (u:User {id: $user_id})
                WITH u
                UNWIND $proficiencies AS prof
                MATCH (target) WHERE target.id = prof.id
                MERGE (u)-[r:HAS_PROFICIENCY]->(target)
                SET r.score = prof.score
                
                // Propagação seletiva: só propaga se o score original for alto (> 0.6)
                WITH u, target, r
                WHERE r.score > 0.6
                MATCH (target)-[:PART_OF]->(c:Competence)<-[:PART_OF]-(related:Skill)
                WHERE NOT (u)-[:HAS_PROFICIENCY]->(related)
                MERGE (u)-[r2:HAS_PROFICIENCY]->(related)
                SET r2.score = r.score * 0.2
                
                WITH u
                UNWIND $answered_ids AS q_id
                MATCH (q:Question {id: q_id})
                MERGE (u)-[:ANSWERED]->(q)
            """, user_id=submission.user_id, proficiencies=proficiencies_data, answered_ids=[a.question_id for a in submission.answers])

    return {"status": "success", "message": "Diagnóstico processado. Auditoria e propagação concluídas."}
