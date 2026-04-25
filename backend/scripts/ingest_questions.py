import os
import json
import time
import argparse
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from neo4j import GraphDatabase
from scripts.init_db import ensure_constraints

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Gemini
client = genai.Client()

# Caminhos de arquivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_PATH = os.path.join(BASE_DIR, "educational_taxonomy.json")
MATRIX_PATH = os.path.join(BASE_DIR, "enem_matrix_full.json")

# Carregar Taxonomia (Tópicos/Áreas)
with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
    EDUCATIONAL_TAXONOMY = json.load(f)

# Carregar Matriz Completa (Competências/Habilidades)
with open(MATRIX_PATH, "r", encoding="utf-8") as f:
    FULL_MATRIX = json.load(f)

# Cache de Subtópicos Dinâmicos
KNOWN_SUBTOPICS = {} # Estrutura: { "Tópico": set(["Subtópico 1", ...]) }

# Configuração Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Ajuste SSL para Aura
uri = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_known_subtopics_from_db():
    """Busca subtópicos já existentes no banco para popular o cache inicial."""
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Topic)<-[:PART_OF]-(s:Subtopic)
            RETURN t.name as topic, s.name as subtopic
        """)
        for record in result:
            topic = record["topic"]
            subtopic = record["subtopic"]
            if topic not in KNOWN_SUBTOPICS:
                KNOWN_SUBTOPICS[topic] = set()
            KNOWN_SUBTOPICS[topic].add(subtopic)

def get_enrichment(question_text, choices, area_hint, current_topic_subtopics, retries=7):
    """Usa o Gemini para enriquecimento pedagógico com alta inteligência taxonômica."""
    
    # Preparar resumo da matriz para a área específica (se possível) para economizar tokens
    area_matrix = [a for a in FULL_MATRIX["areas"] if a["nome"] == area_hint]
    matrix_context = area_matrix if area_matrix else FULL_MATRIX["areas"]

    prompt = f"""
    Analise a seguinte questão do ENEM e forneça um JSON estruturado para enriquecimento pedagógico.
    
    QUESTÃO:
    {question_text}
    
    ALTERNATIVAS:
    {choices}
    
    ---
    REGRAS DE TAXONOMIA (MANDATÓRIO):
    1. AREA e TOPIC: Escolha EXATAMENTE desta lista:
    {json.dumps(EDUCATIONAL_TAXONOMY, indent=2, ensure_ascii=False)}
    
    2. COMPETENCIES e SKILLS: Escolha apenas IDs existentes nesta matriz oficial:
    {json.dumps(matrix_context, indent=2, ensure_ascii=False)}
    
    3. SUBTOPICS (CONSOLIDAÇÃO): 
       Aqui estão subtópicos já conhecidos para esta área/tópico: {list(current_topic_subtopics)}
       - Se a questão se encaixar perfeitamente em um deles, USE O NOME EXATO.
       - Se precisar criar um novo, seja conciso (máx 3 palavras) e use "Title Case".
    
    4. DIAGNÓSTICO: 'is_diagnostic' true apenas para conceitos base (meta: 15% do total).
    
    FORMATO DE RETORNO (JSON APENAS):
    {{
        "explanation": "...",
        "area": "...",
        "topic": "...",
        "subtopics": ["..."],
        "difficulty": "Fácil" | "Médio" | "Difícil",
        "is_diagnostic": boolean,
        "competencies": ["ID_DA_COMPETENCIA"],
        "skills": ["ID_DA_HABILIDADE_SEM_PREFIXO"]
    }}
    
    NOTA: Em 'skills', use apenas o código curto (ex: 'H1'). O sistema fará o link com a competência.
    """
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response.text)
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return None

def ingest_questions(file_path, limit=None):
    # 0. Preparar ambiente
    ensure_constraints()
    get_known_subtopics_from_db()
    
    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    if limit:
        questions = questions[:limit]
        print(f"🔬 Modo Teste: Limitado a {limit} questões.")

    total_questions = len(questions)
    failed_ids = []
    
    print(f"🚀 Iniciando ingestão inteligente de {total_questions} questões...", flush=True)

    with driver.session() as session:
        for index, q in enumerate(questions, 1):
            progress_bar = f"[{index}/{total_questions}] {(index/total_questions)*100:.1f}%"
            
            # 1. Skip check
            result = session.run("MATCH (q:Question {id: $id}) RETURN q.explanation as exp", id=q['id']).single()
            if result and result['exp']:
                continue

            # 2. Obter subtópicos conhecidos para o "chute" de área da questão
            # (ENEM sample costuma vir com área ou podemos inferir pelo ID/Contexto)
            area_hint = q.get('area', '') # Se não tiver, o prompt lida com a matriz completa
            known_for_topic = [] # Será preenchido dinamicamente se soubermos o tópico
            
            # 3. Gemini
            enrichment = get_enrichment(q['question'], q['choices']['text'], area_hint, known_for_topic)
            if not enrichment:
                print(f"❌ {progress_bar} - Falha no Gemini para {q['id']}")
                failed_ids.append(q['id'])
                continue

            # Atualizar cache local de subtópicos
            topic = enrichment.get('topic')
            if topic:
                if topic not in KNOWN_SUBTOPICS: KNOWN_SUBTOPICS[topic] = set()
                KNOWN_SUBTOPICS[topic].update(enrichment.get('subtopics', []))

            # 4. Embedding
            embedding = [0.0] * 768
            try:
                emb_res = client.models.embed_content(
                    model="models/text-embedding-004", # Atualizando para o modelo mais recente de embeddings
                    contents=f"{q['question']} {enrichment['explanation']}",
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )
                embedding = emb_res.embeddings[0].values
            except Exception as e:
                print(f"Erro Embedding: {e}")
                pass

            # 5. DB Write
            try:
                session.execute_write(ingest_tx, q, enrichment, embedding)
                print(f"✅ {progress_bar} - ID: {q['id']} - {enrichment['area']} > {enrichment['topic']}", flush=True)
            except Exception as e:
                print(f"❌ {progress_bar} - Erro DB para {q['id']}: {e}")
                failed_ids.append(q['id'])
            
            time.sleep(0.5)

    if failed_ids:
        print(f"\n⚠️ Finalizado com {len(failed_ids)} falhas.")

def ingest_tx(tx, q, enrichment, embedding):
    choices = q.get('choices', {})
    option_texts = {label: text for label, text in zip(choices.get('label', []), choices.get('text', []))}
    
    # Query Refatorada para ser RESILIENTE
    # Separamos a criação da questão da busca de competências para evitar que um MATCH falho mate a transação
    
    # Parte 1: Questão, Área, Tópicos e Subtópicos (Sempre criados)
    tx.run("""
        MERGE (q:Question {id: $id})
        SET q.text = $text,
            q.answer = $answer,
            q.explanation = $explanation,
            q.difficulty = $difficulty,
            q.is_diagnostic = $is_diagnostic,
            q.embedding = $embedding,
            q.option_a = $opt_a, q.option_b = $opt_b, q.option_c = $opt_c, q.option_d = $opt_d, q.option_e = $opt_e
        
        WITH q
        MERGE (a:Area {name: $area})
        MERGE (t:Topic {name: $topic})
        MERGE (t)-[:BELONGS_TO]->(a)
        
        WITH q, t
        UNWIND $subtopics as subname
        MERGE (s:Subtopic {name: subname})
        MERGE (q)-[:COVERS_TOPIC]->(s)
        MERGE (s)-[:PART_OF]->(t)
    """, id=q['id'], text=q['question'], answer=q['answerKey'], explanation=enrichment['explanation'],
       difficulty=enrichment['difficulty'], is_diagnostic=enrichment['is_diagnostic'], embedding=embedding,
       area=enrichment['area'], topic=enrichment['topic'], subtopics=enrichment['subtopics'],
       opt_a=option_texts.get('A', ''), opt_b=option_texts.get('B', ''), opt_c=option_texts.get('C', ''),
       opt_d=option_texts.get('D', ''), opt_e=option_texts.get('E', ''))

    # Parte 2: Competências (Safe Match)
    for comp_id in enrichment.get('competencies', []):
        tx.run("""
            MATCH (q:Question {id: $qid})
            MATCH (c:Competence {id: $cid})
            MERGE (q)-[:REQUIRES_COMPETENCE]->(c)
        """, qid=q['id'], cid=comp_id)

    # Parte 3: Habilidades (Safe Match com ID composto)
    for skill_code in enrichment.get('skills', []):
        # Tentamos casar com qualquer competência sugerida
        for comp_id in enrichment.get('competencies', []):
            skill_unique_id = f"{comp_id}_{skill_code}"
            tx.run("""
                MATCH (q:Question {id: $qid})
                MATCH (s:Skill {id: $sid})
                MERGE (q)-[:EVALUATES]->(s)
            """, qid=q['id'], sid=skill_unique_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--file", type=str, default=os.path.join(BASE_DIR, "enem_sample.json"))
    args = parser.parse_args()
    ingest_questions(args.file, limit=args.limit)
    driver.close()
