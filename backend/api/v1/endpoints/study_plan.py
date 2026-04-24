from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
import google.generativeai as genai
import os
import json

router = APIRouter()

@router.get("/")
async def get_study_plan(current_user: User = Depends(get_current_user)):
    driver = get_driver()
    with driver.session() as session:
        # 1. Buscar proficiências do usuário
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

        # 2. Gerar Plano de Estudos com Gemini
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
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        try:
            return json.loads(response.text)
        except:
            # Fallback em caso de erro na resposta da IA
            return {"status": "error", "message": "Não foi possível gerar o plano no momento."}
