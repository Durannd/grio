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
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

# Configuração Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_vector_index(session):
    """Cria o índice vetorial no Neo4j 5.x se não existir."""
    print("Configurando índice vetorial no Neo4j...")
    session.run("""
    CREATE VECTOR INDEX question_embeddings IF NOT EXISTS
    FOR (q:Question) ON (q.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 768,
      `vector.similarity_function`: 'cosine'
    }}
    """)

def get_enrichment(question_text, choices):
    """Usa o Gemini para explicar a questão e classificar subtópicos."""
    prompt = f"""
    Analise a seguinte questão do ENEM e forneça um JSON com:
    1. 'explanation': Uma explicação pedagógica passo a passo da resolução.
    2. 'subtopics': Uma lista de subtópicos específicos (ex: ['Cinemática', 'Movimento Uniforme']).
    3. 'difficulty': Uma string ('Fácil', 'Médio', 'Difícil').
    4. 'is_diagnostic': Um booleano indicando se esta questão é excelente para testar o conhecimento base de um aluno.

    QUESTÃO:
    {question_text}
    
    ALTERNATIVAS:
    {choices}
    
    Responda APENAS o JSON puro, sem markdown ou explicações extras.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return None

def ingest_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    with driver.session() as session:
        create_vector_index(session)
        
        for q in questions[:10]:  # Testando com as primeiras 10 questões
            print(f"Processando questão {q['id']}...")
            
            enrichment = get_enrichment(q['question'], q['choices']['text'])
            if not enrichment:
                continue
            
            # Aqui geraríamos o embedding real. 
            # Por enquanto usaremos um vetor fake ou chamaremos o modelo de embedding do Gemini.
            # O modelo 'text-embedding-004' do Gemini gera 768 dimensões.
            try:
                embedding_response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=q['question'] + " " + enrichment['explanation'],
                    task_type="retrieval_document"
                )
                embedding = embedding_response['embedding']
            except Exception as e:
                print(f"Erro no Embedding: {e}")
                embedding = [0.0] * 768

            # Inserir no Neo4j
            session.execute_write(ingest_tx, q, enrichment, embedding)
            print(f"Questão {q['id']} inserida com sucesso.")
            time.sleep(1) # Rate limit safety

def ingest_tx(tx, q, enrichment, embedding):
    # Criar Questão
    query = """
    MERGE (q:Question {id: $id})
    SET q.text = $text,
        q.answer = $answer,
        q.explanation = $explanation,
        q.difficulty = $difficulty,
        q.is_diagnostic = $is_diagnostic,
        q.embedding = $embedding
    WITH q
    UNWIND $subtopics as subtopic_name
    MERGE (s:Subtopic {name: subtopic_name})
    MERGE (q)-[:COVERS_TOPIC]->(s)
    """
    tx.run(query, 
           id=q['id'], 
           text=q['question'], 
           answer=q['answerKey'],
           explanation=enrichment['explanation'],
           difficulty=enrichment['difficulty'],
           is_diagnostic=enrichment['is_diagnostic'],
           embedding=embedding,
           subtopics=enrichment['subtopics'])

if __name__ == "__main__":
    ingest_questions("backend/scripts/enem_sample.json")
    driver.close()
