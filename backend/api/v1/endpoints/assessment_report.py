from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from models.assessment import AssessmentAttempt
from sqlalchemy.orm import Session
from database import get_db
import os
import json
from google import genai
from google.genai import types
from core.translator import get_friendly_name, mask_id, get_friendly_code

router = APIRouter()

def generate_ai_analysis(proficiencies: list):
    """Helper to generate AI analysis from proficiencies list"""
    if not proficiencies:
        return None

    prof_summary = "\n".join([
        f"- [{p.get('area', 'Geral')}] {get_friendly_name(p['id'])}: {p['score']*100:.1f}% - {p['description']}"
        for p in proficiencies
    ])    
    prompt = f"""
    Você é um assistente de análise pedagógica especializado no ENEM.
    Sua tarefa é converter dados técnicos de proficiência em recomendações diagnósticas objetivas.
    
    PERFIL DE PROFICIÊNCIA DO ESTUDANTE:
    {prof_summary}
    
    Instruções para o retorno (JSON):
    1. 'title': Utilize um título técnico para o relatório.
    2. 'summary': Analise a maturidade cognitiva demonstrada pelos dados.
    3. 'strengths': Liste competências com alto nível de domínio técnico.
    4. 'weaknesses': Identifique lacunas fundamentais que impactam o progresso global.
    5. 'action_plan': Defina uma estratégia técnica prioritária.
    6. 'REGRAS': TOM neutro e profissional. Proibido o uso de emojis, saudações ou personificações.

    FORMATO JSON:
    {{
      "title": "string",
      "summary": "string",
      "strengths": ["string"],
      "weaknesses": ["string"],
      "action_plan": "string"
    }}
    """
    
    client = genai.Client()
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return {
            "title": "Diagnóstico Griô", 
            "summary": "Ocorreu um erro ao gerar a análise detalhada, mas seus dados estão salvos.", 
            "strengths": [], 
            "weaknesses": [], 
            "action_plan": "Continue explorando os módulos para acumular mais dados."
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
