from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from models.assessment import AssessmentAttempt
from sqlalchemy.orm import Session
from database import get_db
import os
import json
from core.genai import get_genai_client
from google.genai import types
from core.translator import get_friendly_name, mask_id, get_friendly_code

router = APIRouter()

def generate_ai_analysis(proficiencies: list):
    """Helper to generate AI analysis from proficiencies list using centralized GenAI client"""
    if not proficiencies:
        return None

    prof_summary = "\n".join([
        f"- [{p.get('area', 'Geral')}] {get_friendly_name(p['id'])}: {p['score']*100:.1f}% - {p['description']}"
        for p in proficiencies
    ])    
    
    # Prompt otimizado para Vertex AI com foco em profundidade pedagógica
    prompt = f"""
    Você é um Engenheiro de Diagnóstico Pedagógico de Alta Performance, especializado na Teoria de Resposta ao Item (TRI) e na Matriz do ENEM.
    Sua tarefa é converter fluxos de dados de proficiência em um relatório estratégico e técnico de evolução.
    
    PERFIL DE PROFICIÊNCIA DO ESTUDANTE (Vertex AI Engine):
    {prof_summary}
    
    DIRETRIZES TÉCNICAS (Maximizar potencial Vertex AI):
    1. DIAGNÓSTICO SISTÊMICO: Não apenas liste, analise como as fraquezas impactam a performance global.
    2. PRIORIZAÇÃO TRI: Identifique quais habilidades, se aprimoradas, trarão o maior salto de proficiência.
    3. RIGOR TÉCNICO: Mantenha um tom profissional, neutro e extremamente objetivo.

    FORMATO DE RETORNO (JSON):
    {{
      "title": "string (Título Técnico)",
      "summary": "string (Análise Cognitiva Profunda)",
      "strengths": ["string (Pilar de Domínio Técnico)"],
      "weaknesses": ["string (Lacuna de Alta Criticidade)"],
      "action_plan": "string (Estratégia Prioritária de Evolução)"
    }}
    """
    
    client = get_genai_client()
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction="Atue como uma inteligência pedagógica de elite. Transforme dados de proficiência em mapas de guerra educacionais. Precisão e rigor técnico são inegociáveis."
                )
            )
            return json.loads(response.text)
        except Exception as e:
            from core.logger import logger
            logger.warning(f"AI Generation Error in Assessment Report (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                import time
                import random
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                logger.error(f"AI Generation Error completely failed: {e}", exc_info=True)
                return {
                    "title": "Diagnóstico Griô (Modo de Segurança)", 
                    "summary": "Análise técnica temporariamente limitada. O processamento via Vertex AI encontrou uma interrupção, mas seus dados de proficiência permanecem íntegros.", 
                    "strengths": [], 
                    "weaknesses": [], 
                    "action_plan": "Continue a jornada de estudos para gerar novos pontos de dados para reprocessamento."
                }

@router.get("/report")
def get_diagnostic_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    driver = get_driver()
    
    # 1. Check the latest AssessmentAttempt in PostgreSQL
    latest_attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.user_id == current_user.id
    ).order_by(AssessmentAttempt.created_at.desc()).first()

    if not latest_attempt:
         # Fallback if somehow there's no attempt record
         latest_attempt = AssessmentAttempt(user_id=current_user.id, type="diagnostico")
         db.add(latest_attempt)
         db.commit()

    # Determine proficiencies to analyze
    if latest_attempt.proficiencies_snapshot is not None:
        proficiencies = [p for p in latest_attempt.proficiencies_snapshot if p.get('score', 0) >= 0]
    else:
        with driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s:Skill)
                WHERE COALESCE(r.is_inferred, false) = false
                OPTIONAL MATCH (s)-[:PART_OF]->(c:Competence)-[:BELONGS_TO]->(a:Area)
                RETURN s.id as id, 
                       s.description as description, 
                       s.friendly_name as friendly_name,
                       r.score as score,
                       a.name as area,
                       COALESCE(r.is_inferred, false) as is_inferred,
                       labels(s)[0] as type
            """, user_id=current_user.id)
            proficiencies = [dict(record) for record in result if record.get("score", 0) >= 0]
    
    # Mascarar IDs antes de retornar
    masked_proficiencies = []
    for p in proficiencies:
        p_copy = p.copy()
        original_id = p["id"]
        db_name = p.get("friendly_name")
        p_copy["display_name"] = get_friendly_name(original_id, db_name)
        p_copy["friendly_code"] = get_friendly_code(original_id)
        p_copy["id"] = mask_id(original_id)
        masked_proficiencies.append(p_copy)

    if latest_attempt.analysis_json and latest_attempt.proficiencies_snapshot is not None:
        # NOTE: We still pass the filtered proficiencies here. The snapshot in DB remains complete.
        return {
            "status": "success",
            "analysis": latest_attempt.analysis_json,
            "proficiencies": masked_proficiencies,
            "summary_stats": {
                "total_skills_mapped": len(masked_proficiencies),
                "average_score": sum([p['score'] for p in masked_proficiencies]) / len(masked_proficiencies) if masked_proficiencies else 0
            },
            "snapshot": "historical" 
        }

    if not proficiencies:
        return {"status": "pending", "message": "Nenhum diagnóstico com domínio identificado ainda."}

    # 3. Generate AI Analysis
    analysis_data = generate_ai_analysis(proficiencies)

    # 4. Save to SQL Database
    latest_attempt.analysis_json = analysis_data
    latest_attempt.proficiencies_snapshot = proficiencies
    
    current_user.is_diagnostic_completed = True
    db.add(latest_attempt)
    db.add(current_user)
    db.commit()

    # Mascarar IDs antes de retornar no fluxo de 'new'
    masked_new_proficiencies = []
    for p in proficiencies:
        p_copy = p.copy()
        original_id = p["id"]
        p_copy["display_name"] = get_friendly_name(original_id)
        p_copy["friendly_code"] = get_friendly_code(original_id)
        p_copy["id"] = mask_id(original_id)
        masked_new_proficiencies.append(p_copy)

    return {
        "status": "success",
        "analysis": analysis_data,
        "proficiencies": masked_new_proficiencies,
        "summary_stats": {
            "total_skills_mapped": len(masked_new_proficiencies),
            "average_score": sum([p['score'] for p in masked_new_proficiencies]) / len(masked_new_proficiencies) if masked_new_proficiencies else 0
        },
        "snapshot": "new"
    }

@router.get("/history")
def get_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.user_id == current_user.id
    ).order_by(AssessmentAttempt.created_at.desc()).all()
    
    return {
        "history": [
            {
                "id": a.id,
                "created_at": a.created_at,
                "type": a.type,
                "has_analysis": bool(a.analysis_json)
            } for a in attempts
        ]
    }

@router.get("/history/{attempt_id}")
def get_assessment_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.id == attempt_id,
        AssessmentAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Tentativa não encontrada")
        
    proficiencies = [p for p in (attempt.proficiencies_snapshot or []) if p.get('score', 0) >= 0]

    # Se não tem análise mas tem proficiências, gera agora (Lazy Loading)
    if not attempt.analysis_json and proficiencies:
        attempt.analysis_json = generate_ai_analysis(proficiencies)
        db.add(attempt)
        db.commit()
    
    # Mascarar IDs no histórico e adicionar nomes amigáveis
    masked_proficiencies = []
    for p in proficiencies:
        p_copy = p.copy()
        original_id = p["id"]
        p_copy["display_name"] = get_friendly_name(original_id)
        p_copy["friendly_code"] = get_friendly_code(original_id)
        p_copy["id"] = mask_id(original_id)
        masked_proficiencies.append(p_copy)
    
    return {
        "status": "success",
        "id": attempt.id,
        "created_at": attempt.created_at,
        "type": attempt.type,
        "analysis": attempt.analysis_json,
        "proficiencies": masked_proficiencies,
        "summary_stats": {
            "total_skills_mapped": len(masked_proficiencies),
            "average_score": sum([p['score'] for p in masked_proficiencies]) / len(masked_proficiencies) if masked_proficiencies else 0

        },
        "snapshot": "historical"
    }
