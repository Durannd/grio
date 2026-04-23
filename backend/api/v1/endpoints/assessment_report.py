from fastapi import APIRouter, Depends, HTTPException
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
import os
import google.generativeai as genai

# Configurar Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

@router.get("/report")
def get_diagnostic_report(
    current_user: User = Depends(get_current_user)
):
    driver = get_driver()
    with driver.session() as session:
        # 0. Verificar se já existe uma análise cacheada para evitar chamadas redundantes ao Gemini
        import json
        user_record = session.run("""
            MATCH (u:User {id: $user_id})
            RETURN u.latest_analysis as latest_analysis, u.proficiencies_snapshot as snapshot
        """, user_id=current_user.id).single()
        
        if user_record and user_record["latest_analysis"]:
            try:
                # Se tiver cache, retorna direto
                cached_data = json.loads(user_record["latest_analysis"])
                return cached_data
            except:
                pass

        # 1. Buscar proficiências do usuário (Habilidades e Competências)
        result = session.run("""
            MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(target)
            RETURN target.id as id, 
                   target.description as description, 
                   r.score as score,
                   labels(target)[0] as type
        """, user_id=current_user.id)
        
        proficiencies = [dict(record) for record in result if record["score"] > 0]
        
        if not proficiencies:
            return {"status": "pending", "message": "Nenhum diagnóstico com domínio identificado ainda."}

        # 2. Gerar Resumo da IA
        # Consolidar dados para o prompt
        prof_summary = "\n".join([f"- {p['id']} ({p['description']}): {p['score']*100:.1f}%" for p in proficiencies if p['type'] == 'Skill'])
        
        prompt = f"""
        Como um especialista pedagógico em exames de larga escala (ENEM), forneça uma análise técnica e objetiva do perfil de proficiência deste estudante.
        
        DADOS DE PROFICIÊNCIA:
        {prof_summary}
        
        Retorne um objeto JSON com a seguinte estrutura:
        {{
          "title": "Título curto da análise",
          "summary": "Resumo técnico de 2 parágrafos",
          "strengths": ["Lista de 3 a 5 pontos fortes baseados nos dados"],
          "weaknesses": ["Lista de 3 a 5 lacunas identificadas"],
          "action_plan": "Breve descrição de como as trilhas serão estruturadas"
        }}
        """
        
        model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            generation_config={"response_mime_type": "application/json"}
        )
        ai_response = model.generate_content(prompt)
        
        try:
            analysis_data = json.loads(ai_response.text)
        except:
            # Fallback em caso de erro no JSON
            analysis_data = {
                "title": "Análise de Desempenho",
                "summary": ai_response.text,
                "strengths": [],
                "weaknesses": [],
                "action_plan": "Personalizando trilhas..."
            }

        response_data = {
            "status": "success",
            "analysis": analysis_data,
            "proficiencies": proficiencies,
            "summary_stats": {
                "total_skills_mapped": len([p for p in proficiencies if p['type'] == 'Skill']),
                "average_score": sum([p['score'] for p in proficiencies]) / len(proficiencies) if proficiencies else 0
            }
        }

        # 3. Cachear o resultado no Neo4j para futuras consultas
        session.run("""
            MATCH (u:User {id: $user_id})
            SET u.latest_analysis = $analysis
        """, user_id=current_user.id, analysis=json.dumps(response_data))

        return response_data
