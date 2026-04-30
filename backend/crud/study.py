from neo4j import Driver
from google import genai
from google.genai import types
import os
import json
from datetime import datetime, timedelta
from core.translator import get_friendly_code

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
        Você é um professor especialista que cria micro-aulas para estudantes do ENEM.
        Gere uma explicação didática sobre o tema descrito abaixo.

        TEMA: {result['description']}
        ÁREA DO CONHECIMENTO: {result['area']}

        CONTEXTO INTERNO (USE APENAS COMO REFERÊNCIA, NÃO CITE):
        {knowledge_base if knowledge_base else "Sem exemplos disponíveis."}

        REGRAS OBRIGATÓRIAS:
        1. TITULO_AMIGAVEL: Crie um nome curto e claro (2-4 palavras) que resuma o tema para um aluno.
           Exemplos: "Geometria Plana", "Cinemática Básica", "Interpretação de Gráficos".
           NÃO use siglas, códigos ou identificadores técnicos.
        2. CONTEUDO: Micro-aula em Markdown bem formatado.
           - Use títulos (##), listas, **negrito** para conceitos-chave e > para dicas.
           - Linguagem clara, direta e acessível para ensino médio.
           - Inclua exemplos práticos ORIGINAIS (NÃO copie os exercícios do contexto).
        3. PROIBIDO:
           - Citar, reproduzir ou referenciar os exercícios/questões do contexto interno.
           - Mencionar códigos de habilidade (como MT_C1_H01, H23, etc.).
           - Saudações, personificações ou frases como "Olá, aluno!".
           - Começar com o título da habilidade (o sistema já exibe isso).

        FORMATO JSON:
        {{
          "titulo_amigavel": "string (2-4 palavras)",
          "conteudo_markdown": "string (Markdown formatado, começando com ## subtítulo)"
        }}
        """

        max_retries = 3
        base_delay = 2 # seconds
        
        for attempt in range(max_retries):
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
                break # Success, exit loop
            except Exception as e:
                from core.logger import logger
                logger.warning(f"Gemini microlesson generation failed (attempt {attempt + 1}/{max_retries}) for {skill_id}: {e}")
                
                if attempt < max_retries - 1:
                    import time
                    import random
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    logger.error(f"Gemini microlesson generation completely failed after {max_retries} attempts for {skill_id}: {e}")
                    raise ValueError("GEMINI_API_BUSY")

        # Persistir no Neo4j somente em caso de sucesso
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
