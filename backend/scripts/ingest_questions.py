import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Configuração Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_vector_index(session, dimension=768):
    """Cria ou recria o índice vetorial e índices de performance."""
    print(f"⚙️ Configurando índices de performance e vetor (Dim: {dimension})...")
    
    # Índices de Performance (Essenciais para velocidade)
    indices = [
        "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
        "CREATE CONSTRAINT subtopic_name IF NOT EXISTS FOR (s:Subtopic) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT skill_code IF NOT EXISTS FOR (sk:Skill) REQUIRE sk.code IS UNIQUE",
        "CREATE CONSTRAINT comp_id IF NOT EXISTS FOR (c:Competence) REQUIRE c.id IS UNIQUE"
    ]
    
    for cmd in indices:
        try:
            session.run(cmd)
        except:
            pass

    # Índice Vetorial
    try:
        session.run("DROP INDEX question_embeddings IF EXISTS")
    except:
        pass
        
    session.run(f"""
    CREATE VECTOR INDEX question_embeddings IF NOT EXISTS
    FOR (q:Question) ON (q.embedding)
    OPTIONS {{indexConfig: {{
      `vector.dimensions`: {dimension},
      `vector.similarity_function`: 'cosine'
    }}}}
    """)

import re

def get_enrichment(question_text, choices, retries=7):
    """Usa o Gemini para enriquecimento pedagógico com alta resiliência."""
    prompt = f"""
    Analise a seguinte questão do ENEM e forneça um JSON estruturado para enriquecimento pedagógico.
    
    QUESTÃO:
    {question_text}
    
    ALTERNATIVAS:
    {choices}
    
    CRITÉRIOS PARA 'is_diagnostic':
    - Marque como `true` APENAS se a questão testar um conceito FUNDAMENTAL e ESTRUTURANTE.
    - Meta: Apenas ~15% das questões diagnósticas.
    
    FORMATO DE RETORNO (JSON APENAS):
    {{
        "explanation": "Explicação passo a passo.",
        "subtopics": ["lista", "de", "subtópicos"],
        "difficulty": "Fácil" | "Médio" | "Difícil",
        "is_diagnostic": boolean,
        "skills": ["H1", "H17"],
        "competencies": ["CN_C1", "MT_C3"]
    }}
    """
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            # Limpeza robusta do JSON usando Regex
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response.text)
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                wait_time = (attempt + 1) * 5 # Espera progressiva: 5s, 10s, 15s...
                print(f"⚠️ [{attempt+1}/{retries}] API instável (503/429). Aguardando {wait_time}s...")
                time.sleep(wait_time)
            elif attempt < retries - 1:
                print(f"⚠️ [{attempt+1}/{retries}] Erro inesperado. Tentando novamente em 2s...")
                time.sleep(2)
            else:
                print(f"❌ Falha persistente após {retries} tentativas: {e}")
                return None

def ingest_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_questions = len(questions)
    failed_ids = []
    
    print(f"🚀 Iniciando ingestão de {total_questions} questões...")

    with driver.session() as session:
        # Usamos 768 para o modelo text-embedding-004
        create_vector_index(session, dimension=768)
        
        for index, q in enumerate(questions, 1):
            percent = (index / total_questions) * 100
            progress_bar = f"[{index}/{total_questions}] {percent:.1f}%"
            
            # 1. Verificar se a questão já foi processada
            result = session.run("MATCH (q:Question {id: $id}) RETURN q.explanation as exp", id=q['id']).single()
            if result and result['exp']:
                # print(f"{progress_bar} - Questão {q['id']} já existe. Pulando...")
                continue

            print(f"{progress_bar} - Processando ID: {q['id']}...")
            
            # 2. Obter Enriquecimento (com Retries)
            enrichment = get_enrichment(q['question'], q['choices']['text'])
            if not enrichment:
                print(f"❌ [{index}] Falha crítica no enriquecimento para ID {q['id']}")
                failed_ids.append(q['id'])
                continue
            
            # 3. Embedding Real (com Retry simples)
            embedding = None
            for emb_attempt in range(3):
                try:
                    embedding_response = genai.embed_content(
                        model="models/gemini-embedding-001",
                        content=f"{q['question']} {enrichment['explanation']}",
                        task_type="retrieval_document"
                    )
                    embedding = embedding_response['embedding']
                    break
                except Exception as e:
                    print(f"⚠️ [{index}] Tentativa de embedding {emb_attempt + 1} falhou: {e}")
                    time.sleep(1)
            
            if not embedding:
                print(f"⚠️ [{index}] Usando vetor nulo para {q['id']} após falhas de embedding.")
                embedding = [0.0] * 768

            # 4. Inserir no Neo4j
            try:
                session.execute_write(ingest_tx, q, enrichment, embedding)
            except Exception as e:
                print(f"❌ [{index}] Erro no Banco para {q['id']}: {e}")
                failed_ids.append(q['id'])
            
            time.sleep(1) # Delay mais seguro para Rate Limit

    if failed_ids:
        with open("scripts/failed_ingestions.log", "w") as f_log:
            f_log.write("\n".join(map(str, failed_ids)))
        print(f"\n⚠️ Ingestão finalizada com {len(failed_ids)} falhas. Veja scripts/failed_ingestions.log")
    else:
        print("\n🏆 Ingestão concluída com 100% de sucesso!")


def ingest_tx(tx, q, enrichment, embedding):
    # Extrair opções do formato ENEM
    choices = q.get('choices', {})
    option_texts = {label: text for label, text in zip(choices.get('label', []), choices.get('text', []))}
    
    # Criar Questão
    query = """
    MERGE (q:Question {id: $id})
    SET q.text = $text,
        q.answer = $answer,
        q.explanation = $explanation,
        q.difficulty = $difficulty,
        q.is_diagnostic = $is_diagnostic,
        q.embedding = $embedding,
        q.option_a = $opt_a,
        q.option_b = $opt_b,
        q.option_c = $opt_c,
        q.option_d = $opt_d,
        q.option_e = $opt_e
    WITH q
    UNWIND $subtopics as subtopic_name
    MERGE (s:Subtopic {name: subtopic_name})
    MERGE (q)-[:COVERS_TOPIC]->(s)
    
    WITH q
    UNWIND $skills as skill_code
    MATCH (sk:Skill {code: skill_code})
    MERGE (q)-[:EVALUATES]->(sk)

    WITH q
    UNWIND $competencies as comp_id
    MATCH (c:Competence {id: comp_id})
    MERGE (q)-[:REQUIRES_COMPETENCE]->(c)
    """
    tx.run(query, 
           id=q['id'], 
           text=q['question'], 
           answer=q['answerKey'],
           explanation=enrichment['explanation'],
           difficulty=enrichment['difficulty'],
           is_diagnostic=enrichment['is_diagnostic'],
           embedding=embedding,
           subtopics=enrichment['subtopics'],
           skills=enrichment.get('skills', []),
           competencies=enrichment.get('competencies', []),
           opt_a=option_texts.get('A', ''),
           opt_b=option_texts.get('B', ''),
           opt_c=option_texts.get('C', ''),
           opt_d=option_texts.get('D', ''),
           opt_e=option_texts.get('E', ''))

if __name__ == "__main__":
    ingest_questions("scripts/enem_sample.json")
    driver.close()
