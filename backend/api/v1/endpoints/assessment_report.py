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

router = APIRouter()

@router.get("/report")
def get_diagnostic_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    driver = get_driver()
    with driver.session() as session:
        # 1. Buscar proficiências atuais do usuário
        result = session.run("""
            MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s:Skill)
            OPTIONAL MATCH (s)-[:PART_OF]->(c:Competence)-[:BELONGS_TO]->(a:Area)
            RETURN s.id as id, 
                   s.description as description, 
                   r.score as score,
                   a.name as area,
                   labels(s)[0] as type
        """, user_id=current_user.id)
        
        proficiencies = [dict(record) for record in result if record["score"] > 0]
        
        if not proficiencies:
            return {"status": "pending", "message": "Nenhum diagnóstico com domínio identificado ainda."}

        # 2. Check the latest AssessmentAttempt in PostgreSQL
        latest_attempt = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.user_id == current_user.id
        ).order_by(AssessmentAttempt.created_at.desc()).first()

        if not latest_attempt:
             # Fallback if somehow there's no attempt record
             latest_attempt = AssessmentAttempt(user_id=current_user.id, type="diagnostico")
             db.add(latest_attempt)
             db.commit()

        # If the latest attempt already has an analysis, return it directly
        if latest_attempt.analysis_json and latest_attempt.proficiencies_snapshot:
            return {
                "status": "success",
                "analysis": latest_attempt.analysis_json,
                "proficiencies": latest_attempt.proficiencies_snapshot,
                "summary_stats": {
                    "total_skills_mapped": len(latest_attempt.proficiencies_snapshot),
                    "average_score": sum([p['score'] for p in latest_attempt.proficiencies_snapshot]) / len(latest_attempt.proficiencies_snapshot) if latest_attempt.proficiencies_snapshot else 0
                },
                "snapshot": "historical" 
            }

        # 3. Gerar Nova Análise com IA (Since it's a new attempt without analysis)
        prof_summary = "\n".join([f"- [{p.get('area', 'Geral')}] {p['id']}: {p['score']*100:.1f}% - {p['description']}" for p in proficiencies])
        
        prompt = f"""
        Você é o analista pedagógico do sistema Griô.
        Sua missão é transformar dados técnicos em recomendações estratégicas para o estudante.
        
        PERFIL DE PROFICIÊNCIA DO ESTUDANTE:
        {prof_summary}
        
        Instruções para o retorno (JSON):
        1. 'title': Use um título técnico para o diagnóstico de proficiência.
        2. 'summary': Analise a intersecção entre as áreas. Não apenas liste dados. Fale sobre a maturidade cognitiva.
        3. 'strengths': Liste competências onde o aluno já brilha.
        4. 'weaknesses': Identifique lacunas 'âncora' (aquelas que impedem o avanço em outros temas).
        5. 'action_plan': Sugira uma estratégia de estudo prioritária.
        6. 'EMOJIS': Proibido o uso de emojis em qualquer campo do JSON.

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
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        try:
            analysis_data = json.loads(response.text)
        except:
            analysis_data = {"title": "Diagnóstico Griô", "summary": response.text, "strengths": [], "weaknesses": [], "action_plan": "Continue explorando os módulos."}

        response_data = {
            "status": "success",
            "analysis": analysis_data,
            "proficiencies": proficiencies,
            "summary_stats": {
                "total_skills_mapped": len(proficiencies),
                "average_score": sum([p['score'] for p in proficiencies]) / len(proficiencies) if proficiencies else 0
            },
            "snapshot": "new"
        }

        # 4. Save to SQL Database Attempt instead of Neo4j Cache
        latest_attempt.analysis_json = analysis_data
        latest_attempt.proficiencies_snapshot = proficiencies
        
        current_user.is_diagnostic_completed = True
        db.add(latest_attempt)
        db.add(current_user)
        db.commit()

        return response_data

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
        
    proficiencies = attempt.proficiencies_snapshot or []
    
    return {
        "status": "success",
        "id": attempt.id,
        "created_at": attempt.created_at,
        "type": attempt.type,
        "analysis": attempt.analysis_json,
        "proficiencies": proficiencies,
        "summary_stats": {
            "total_skills_mapped": len(proficiencies),
            "average_score": sum([p['score'] for p in proficiencies]) / len(proficiencies) if proficiencies else 0
        },
        "snapshot": "historical"
    }
