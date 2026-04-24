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

        # 2. Verificar Cache (Snapshot)
        import json
        import hashlib
        
        # Criar um hash das proficiências atuais para o snapshot
        prof_string = json.dumps(sorted(proficiencies, key=lambda x: x['id']), sort_keys=True)
        current_snapshot = hashlib.md5(prof_string.encode()).hexdigest()
        
        user_record = session.run("""
            MATCH (u:User {id: $user_id})
            RETURN u.latest_analysis as latest_analysis, u.proficiencies_snapshot as snapshot
        """, user_id=current_user.id).single()
        
        if user_record and user_record["snapshot"] == current_snapshot and user_record["latest_analysis"]:
            try:
                return json.loads(user_record["latest_analysis"])
            except:
                pass

        # 3. Gerar Nova Análise com IA
        prof_summary = "\n".join([f"- [{p.get('area', 'Geral')}] {p['id']}: {p['score']*100:.1f}% - {p['description']}" for p in proficiencies])
        
        prompt = f"""
        Você é o Mentor Griô, um mestre em pedagogia e análise de dados do ENEM.
        Sua missão é transformar dados técnicos em um caminho de luz para o estudante.
        
        PERFIL DE PROFICIÊNCIA DO ESTUDANTE:
        {prof_summary}
        
        Instruções para o retorno (JSON):
        1. 'title': Use algo inspirador mas profissional.
        2. 'summary': Analise a intersecção entre as áreas. Não apenas liste dados. Fale sobre a maturidade cognitiva.
        3. 'strengths': Liste competências onde o aluno já brilha.
        4. 'weaknesses': Identifique lacunas 'âncora' (aquelas que impedem o avanço em outros temas).
        5. 'action_plan': Sugira uma estratégia de estudo prioritária.

        FORMATO JSON:
        {{
          "title": "string",
          "summary": "string",
          "strengths": ["string"],
          "weaknesses": ["string"],
          "action_plan": "string"
        }}
        """
        
        model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            generation_config={"response_mime_type": "application/json"}
        )
        ai_response = model.generate_content(prompt)
        
        try:
            analysis_data = json.loads(ai_response.text)
        except:
            analysis_data = {"title": "Sua Jornada Griô", "summary": ai_response.text, "strengths": [], "weaknesses": [], "action_plan": "Continue explorando."}

        response_data = {
            "status": "success",
            "analysis": analysis_data,
            "proficiencies": proficiencies,
            "summary_stats": {
                "total_skills_mapped": len(proficiencies),
                "average_score": sum([p['score'] for p in proficiencies]) / len(proficiencies) if proficiencies else 0
            },
            "snapshot": current_snapshot
        }

        # 4. Salvar no Cache
        session.run("""
            MATCH (u:User {id: $user_id})
            SET u.latest_analysis = $analysis,
                u.proficiencies_snapshot = $snapshot
        """, user_id=current_user.id, analysis=json.dumps(response_data), snapshot=current_snapshot)

        return response_data
