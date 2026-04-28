from neo4j import Driver
from google import genai
from google.genai import types
import os
import json
from datetime import datetime, timedelta

def get_or_generate_microlesson(driver: Driver, skill_id: str):
    with driver.session() as session:
        # 1. Tentar buscar no Neo4j
        result = session.run("""
            MATCH (s:Skill {id: $skill_id})
            OPTIONAL MATCH (s)-[:PART_OF]->(c:Competence)-[:BELONGS_TO]->(a:Area)
            RETURN s.id as id, 
                   s.description as description, 
                   s.content as content,
                   s.friendly_name as friendly_name,
                   s.last_enriched_at as last_enriched_at,
                   a.name as area
        """, skill_id=skill_id).single()

        if not result:
            return None

        # Lógica de Cache (5 anos = 1825 dias)
        is_cache_valid = False
        if result["content"] and result["last_enriched_at"]:
            try:
                last_date = datetime.fromisoformat(result["last_enriched_at"])
                if datetime.now() - last_date < timedelta(days=1825):
                    is_cache_valid = True
            except:
                pass 

        if is_cache_valid:
            return {
                "skill_id": result["id"],
                "friendly_name": result["friendly_name"],
                "description": result["description"],
                "content": result["content"],
                "area": result["area"]
            }

        # 2. Buscar Base de Conhecimento (Questões Reais) para RAG
        questions_result = session.run("""
            MATCH (q:Question)-[:EVALUATES]->(s:Skill {id: $skill_id})
            RETURN q.text as text, q.explanation as explanation
            ORDER BY rand() LIMIT 10
        """, skill_id=skill_id)
        
        knowledge_base = ""
        for i, q_record in enumerate(questions_result, 1):
            knowledge_base += f"EXEMPLO {i}:\n"
            knowledge_base += f"ENUNCIADO: {q_record['text']}\n"
            knowledge_base += f"EXPLICAÇÃO PEDAGÓGICA: {q_record['explanation']}\n\n"

        # 3. Gerar via Gemini
        client = genai.Client()
        
        prompt = f"""
        Você é um assistente de ensino especializado na Matriz de Referência do ENEM.
        Sua tarefa é gerar uma explicação técnica e didática sobre uma Habilidade específica E criar um título amigável para ela.

        HABILIDADE: {result['id']}
        DESCRIÇÃO: {result['description']}
        ÁREA: {result['area']}

        BASE DE CONHECIMENTO (QUESTÕES REAIS DO ENEM):
        {knowledge_base if knowledge_base else "Nenhum exemplo real encontrado para esta habilidade. Baseie-se apenas na descrição."}

        DIRETRIZES:
        1. TITULO_AMIGAVEL: Crie um nome curto (máximo 4 palavras) que resuma o tema central desta habilidade para um aluno (ex: "Geometria Plana", "Cinemática Básica").
        2. CONTEUDO: Explique o conceito de forma técnica, neutra e objetiva. Proibido saudações ou personificações.

        FORMATO JSON:
        {{
          "titulo_amigavel": "string",
          "conteudo_markdown": "string (Markdown formatado)"
        }}
        """

        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            friendly_name = data.get("titulo_amigavel", "Tópico de Estudo")
            content = data.get("conteudo_markdown", "# Erro ao gerar conteúdo")
        except Exception as e:
            print(f"Erro no processamento da IA: {e}")
            friendly_name = "Tópico Especial"
            content = response.text if 'response' in locals() else "Erro técnico na geração."

        # Persistir no Neo4j de forma idempotente
        today = datetime.now().isoformat()
        session.run("""
            MATCH (s:Skill {id: $skill_id})
            SET s.content = $content, 
                s.last_enriched_at = $today,
                s.friendly_name = $friendly_name
        """, skill_id=skill_id, content=content, today=today, friendly_name=friendly_name)

        return {
            "skill_id": result["id"],
            "friendly_name": friendly_name,
            "description": result["description"],
            "content": content,
            "area": result["area"]
        }
