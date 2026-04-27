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
                pass # Caso o formato da data esteja corrompido, gera de novo

        if is_cache_valid:
            return {
                "skill_id": result["id"],
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
        Sua tarefa é gerar uma explicação técnica e didática sobre uma Habilidade específica.

        HABILIDADE: {result['id']}
        DESCRIÇÃO: {result['description']}
        ÁREA: {result['area']}

        BASE DE CONHECIMENTO (QUESTÕES REAIS DO ENEM):
        {knowledge_base if knowledge_base else "Nenhum exemplo real encontrado para esta habilidade. Baseie-se apenas na descrição da habilidade."}

        DIRETRIZES DE CONTEÚDO:
        1. TOM: Estritamente profissional, neutro e objetivo.
        2. LINGUAGEM: Técnica e precisa. Evite qualquer tipo de saudação, personificação ou tratamento informal.
        3. FOCO: Analise as questões fornecidas na Base de Conhecimento para compreender o padrão técnico de avaliação. Explique a fundamentação teórica do conceito e sua aplicação prática baseada nesse padrão.

        FORMATO DA RESPOSTA (Markdown):
        # [Crie um título técnico para a Habilidade, SEM incluir o código. Ex: "Progressão Temática e Estrutura Textual"]
        
        ## Fundamentação Teórica
        (Explique o conceito em 2 parágrafos diretos. Foque em definições, axiomas ou regras fundamentais)
        
        ## Contexto de Avaliação (ENEM)
        (Explique como este conhecimento é testado na prova e qual o processo cognitivo exigido do candidato, citando nuances observadas nos exemplos)
        
        ## Observação Técnica
        (Destaque um ponto de atenção recorrente, uma exceção ou um erro comum na aplicação desta habilidade)

        REGRAS:
        - Máximo de 250 palavras.
        - Use Markdown limpo.
        - Proibido o uso de introduções como "Olá", "Eu sou o...", ou tratamentos como "você", "estudante", "jovem".
        """

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt
        )

        content = response.text

        # 4. Persistir no Neo4j
        today = datetime.now().isoformat()
        session.run("""
            MATCH (s:Skill {id: $skill_id})
            SET s.content = $content, s.last_enriched_at = $today
        """, skill_id=skill_id, content=content, today=today)

        return {
            "skill_id": result["id"],
            "description": result["description"],
            "content": content,
            "area": result["area"]
        }
