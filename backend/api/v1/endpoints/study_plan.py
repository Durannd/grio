from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from database import get_db
from sqlalchemy.orm import Session
from core.genai import get_genai_client
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

    # 2. Verificar Cache no Postgres
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
                WHERE r.score >= 0
                RETURN s.id as id, s.description as description, r.score as score, COALESCE(r.is_inferred, false) as is_inferred
                ORDER BY r.score ASC
                LIMIT 5
            """, user_id=current_user.id)
            
            proficiencies = [dict(record) for record in result]
            
            if not proficiencies:
                return {"status": "pending", "message": "Faça a prova diagnóstica primeiro para gerar seu plano."}

            # 3. Gerar Plano de Estudos via Centralized Client (Vertex AI Optimized)
            prof_summary = "\n".join([f"- {p['id']}: {p['score']*100:.1f}% {'(Inferido)' if p['is_inferred'] else ''} - {p['description']}" for p in proficiencies])
            
            prompt = f"""
            Você é um Arquiteto de Aprendizagem de Alta Performance, especializado em Otimização de Estudos para o ENEM.
            Sua missão é projetar um Plano de Estudos técnico, cirúrgico e focado em ganho real de proficiência (TRI).
            
            FLUXO DE PROFICIÊNCIA DO ESTUDANTE (Vertex AI Engine):
            {prof_summary}
            
            DIRETRIZES TÉCNICAS (Maximizar potencial Vertex AI):
            1. PRIORIZAÇÃO TRI: Lacunas reais (scores baixos sem marcação de inferência) devem ser remediadas IMEDIATAMENTE para estancar a perda de pontos por erros em questões fáceis/médias.
            2. EXPANSÃO DE POTENCIAL: Utilize as habilidades '(Inferido)' como ganchos cognitivos para acelerar a curva de aprendizado em áreas de afinidade.
            3. ESTRATÉGIA CIRÚRGICA: O plano deve ser prático, técnico e livre de qualquer ruído informacional ou saudações.
            
            FORMATO DE RETORNO (JSON):
            {{
              "plan": [
                {{
                  "priority": 1,
                  "skill_code": "string",
                  "title": "string (Título Técnico)",
                  "topics": ["string"],
                  "justification": "string (Análise de Relevância ENEM)",
                  "tip": "string (Dica de Alta Performance)"
                }}
              ],
              "motivation": "string (Síntese Estratégica)"
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
                            system_instruction="Atue como um estrategista educacional sênior. Sua prioridade é a eficiência cognitiva e a maximização da nota TRI através de intervenções precisas."
                        )
                    )
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
                    from core.logger import logger
                    logger.warning(f"Erro ao gerar plano de estudos IA (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        import time
                        import random
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                    else:
                        logger.error(f"Erro crítico ao processar plano de estudos IA: {e}", exc_info=True)
                        raise HTTPException(status_code=503, detail="O servidor de Inteligência Artificial via Vertex AI está com alta demanda. Seus dados estão preservados, tente novamente em alguns instantes.")
