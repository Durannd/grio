import os
import json
import time
import argparse
from dotenv import load_dotenv
from core.genai import get_genai_client
from google.genai import types
from neo4j import GraphDatabase
from pydantic import BaseModel, Field
from scripts.init_db import ensure_constraints

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Centralizada Gemini (Vertex AI Optimized para Ingestão em Lote)
client = get_genai_client()

# Caminhos de arquivos
# ... (rest of imports and configs)
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

# --- SCHEMA PARA SAÍDA ESTRUTURADA ---
class EnrichmentSchema(BaseModel):
    explanation: str = Field(description="Explicação detalhada da resposta correta e dos conceitos envolvidos.")
    area: str = Field(description="Área do conhecimento (ex: Ciências da Natureza e suas Tecnologias).")
    topic: str = Field(description="Tópico principal (ex: Biologia: Ecologia e Meio Ambiente).")
    subtopics: list[str] = Field(description="Lista de subtópicos específicos (ex: ['Ciclos Biogeoquímicos', 'Poluição']).")
    difficulty: str = Field(description="Nível de dificuldade ('Fácil', 'Médio' ou 'Difícil').")
    is_diagnostic: bool = Field(description="Verdadeiro se a questão for fundamental para diagnosticar nivelamento base.")
    competencies: list[str] = Field(description="IDs das competências da matriz de referência (ex: ['C1', 'C2']).")
    skills: list[str] = Field(description="IDs das habilidades sem o prefixo da competência (ex: ['H1', 'H3']).")

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
    Você é um Engenheiro de Dados Educacionais de Alta Performance, especializado na Matriz de Referência do ENEM.
    Sua missão é realizar o enriquecimento pedagógico cirúrgico da questão fornecida para alimentar nosso grafo de conhecimento.
    
    QUESTÃO (Vertex AI Data Stream):
    {question_text}
    
    ALTERNATIVAS:
    {choices}
    
    ---
    DIRETRIZES TÉCNICAS (Maximizar potencial Vertex AI):
    1. TAXONOMIA RÍGIDA: Escolha EXATAMENTE desta lista para AREA e TOPIC:
    {json.dumps(EDUCATIONAL_TAXONOMY, indent=2, ensure_ascii=False)}
    
    2. MAPEAMENTO DE MATRIZ: Utilize apenas IDs existentes nesta matriz oficial:
    {json.dumps(matrix_context, indent=2, ensure_ascii=False)}
    
    3. CONSOLIDAÇÃO DE SUBTÓPICOS: 
       Subtópicos existentes no grafo para esta área: {list(current_topic_subtopics)}
       - REGRA DE OURO: Reutilize subtópicos da lista acima se houver qualquer correlação técnica. Evite fragmentação.
       - SÓ crie um novo subtópico se for um conceito fundamentalmente inédito.
    
    4. PRECISÃO PEDAGÓGICA: A 'explanation' deve ser profunda, clara e focada na resolução lógica da questão.
    
    NOTA: Em 'skills', use apenas o código curto (ex: 'H1'). O sistema fará o link com a competência.
    """
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EnrichmentSchema,
                    temperature=0.2 # Menos criatividade, mais consistência taxonômica
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Tentativa {attempt + 1}/{retries} falhou: {e}")
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

            # 2. Obter subtópicos conhecidos para a área da questão
            area_hint = q.get('area', '')
            current_area_subtopics = set()
            
            # Busca todos os subtópicos já cadastrados nos tópicos desta Área
            if area_hint in EDUCATIONAL_TAXONOMY:
                for t in EDUCATIONAL_TAXONOMY[area_hint]:
                    current_area_subtopics.update(KNOWN_SUBTOPICS.get(t, set()))
            else:
                # Se a área não veio no JSON, pega uma amostra geral (limitada para não estourar tokens)
                for subs in KNOWN_SUBTOPICS.values():
                    current_area_subtopics.update(list(subs)[:5])
            
            # 3. Gemini
            enrichment = get_enrichment(q['question'], q['choices']['text'], area_hint, current_area_subtopics)
            if not enrichment:
                print(f"❌ {progress_bar} - Falha no Gemini para {q['id']}", flush=True)
                failed_ids.append(q['id'])
                continue

            # Atualizar cache local de subtópicos com o tópico retornado
            topic = enrichment.get('topic')
            if topic:
                if topic not in KNOWN_SUBTOPICS: 
                    KNOWN_SUBTOPICS[topic] = set()
                KNOWN_SUBTOPICS[topic].update(enrichment.get('subtopics', []))

            # 4. Embedding
            try:
                emb_res = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=f"{q['question']} {enrichment['explanation']}",
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=768
                    )
                )
                embedding = emb_res.embeddings[0].values
            except Exception as e:
                print(f"❌ {progress_bar} - Erro Embedding para {q['id']}: {e}", flush=True)
                failed_ids.append(q['id'])
                continue # Pula a inserção para não salvar vetor de zeros!

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

    # Parte 2: Competências otimizado com UNWIND
    comps = enrichment.get('competencies', [])
    if comps:
        tx.run("""
            MATCH (q:Question {id: $qid})
            UNWIND $comps as cid
            MATCH (c:Competence {id: cid})
            MERGE (q)-[:REQUIRES_COMPETENCE]->(c)
        """, qid=q['id'], comps=comps)

    # Parte 3: Habilidades otimizado com UNWIND
    skills = enrichment.get('skills', [])
    # Cria os IDs únicos combinando todas as competências com todas as habilidades sugeridas
    skill_ids = [f"{c}_{s}" for c in comps for s in skills]
    if skill_ids:
        tx.run("""
            MATCH (q:Question {id: $qid})
            UNWIND $skill_ids as sid
            MATCH (s:Skill {id: sid})
            MERGE (q)-[:EVALUATES]->(s)
        """, qid=q['id'], skill_ids=skill_ids)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--file", type=str, default=os.path.join(BASE_DIR, "enem_sample.json"))
    args = parser.parse_args()
    ingest_questions(args.file, limit=args.limit)
    driver.close()
