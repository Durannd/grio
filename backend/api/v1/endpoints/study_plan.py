from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
import os
import json

router = APIRouter()

@router.get("/")
async def get_study_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Obter a última tentativa de diagnóstico
    from models.assessment import AssessmentAttempt
    latest_attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.user_id == current_user.id
    ).order_by(AssessmentAttempt.created_at.desc()).first()

    # 2. Verificar Cache no Postgres. O Cache deve ser inválido se:
    # a) O attempt não possuir analysis_json preenchido (ou seja, attempt "novo") mas o cache for antigo?
    # Para ser simples no MVP: vamos amarrar o cache do Study Plan ao AssessmentAttempt
    # Mas como o study_plan_cache tá na tabela de usuários, vamos verificar se o JSON guardado 
    # tem uma chave de `attempt_id`. Se o `attempt_id` for menor que o último, refaz o plano.
    
    use_cache = False
    if current_user.study_plan_cache and latest_attempt:
        try:
            cached_data = json.loads(current_user.study_plan_cache)
            if cached_data.get("attempt_id") == latest_attempt.id:
                use_cache = True
                return cached_data
        except:
            pass

    if not use_cache:
        driver = get_driver()
        with driver.session() as session:
            # 2. Buscar proficiências do usuário
            result = session.run("""
                MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s:Skill)
                WHERE r.score > 0
                RETURN s.id as id, s.description as description, r.score as score
                ORDER BY r.score ASC
                LIMIT 5
            """, user_id=current_user.id)
            
            proficiencies = [dict(record) for record in result]
            
            if not proficiencies:
                return {"status": "pending", "message": "Faça a prova diagnóstica primeiro para gerar seu plano."}

            # 3. Gerar Plano de Estudos com Gemini
            prof_summary = "\n".join([f"- {p['id']}: {p['score']*100:.1f}% - {p['description']}" for p in proficiencies])
            
            prompt = f"""
            Você é um estrategista educacional especializado no ENEM.
            Com base nas proficiências do estudante abaixo (onde menores scores indicam maiores dificuldades), gere um PLANO DE ESTUDOS personalizado.
            
            PROFICIÊNCIAS:
            {prof_summary}
            
            Instruções:
            1. Identifique as 3 maiores lacunas prioritárias.
            2. Para cada lacuna, indique:
               - O que estudar (temas específicos).
               - Por que estudar (relevância para o ENEM).
               - Uma dica prática de estudo.
            3. O tom deve ser motivador, técnico e direto.
            
            FORMATO JSON:
            {{
              "plan": [
                {{
                  "priority": 1,
                  "skill_code": "string",
                  "title": "string",
                  "topics": ["string"],
                  "justification": "string",
                  "tip": "string"
                }}
              ],
              "motivation": "string"
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
                plan_data = json.loads(response.text)
                
                # Associar o plano gerado à última tentativa
                if latest_attempt:
                    plan_data["attempt_id"] = latest_attempt.id
                
                # 4. Salvar no Cache do Postgres
                current_user.study_plan_cache = json.dumps(plan_data)
                db.add(current_user)
                db.commit()
                
                return plan_data
            except Exception as e:
                print(f"Erro ao processar IA: {e}")
                # Fallback em caso de erro na resposta da IA
                return {"status": "error", "message": "Não foi possível gerar o plano no momento."}
