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

def create_vector_index(session):
    """Cria o índice vetorial no Neo4j 5.x se não existir."""
    print("Configurando índice vetorial no Neo4j...")
    session.run("""
    CREATE VECTOR INDEX question_embeddings IF NOT EXISTS
    FOR (q:Question) ON (q.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 3072,
      `vector.similarity_function`: 'cosine'
    }}
    """)

def get_enrichment(question_text, choices):
    """Usa o Gemini para explicar a questão e classificar subtópicos e habilidades ENEM."""
    prompt = f"""
    Analise a seguinte questão do ENEM e forneça um JSON estruturado para enriquecimento pedagógico.
    
    QUESTÃO:
    {question_text}
    
    ALTERNATIVAS:
    {choices}
    
    CRITÉRIOS PARA 'is_diagnostic':
    - Marque como `true` APENAS se a questão testar um conceito FUNDAMENTAL e ESTRUTURANTE (ex: as 4 operações, leis básicas da física, interpretação central).
    - Se a questão exigir aplicação complexa ou cruzamento de muitos temas, use `false`.
    - Meta: Apenas ~15% das questões diagnósticas. Seja RIGOROSO.

    MATRIZ ENEM:
    - Identifique quais Habilidades (H1 a H30) e Competências de Área (ex: CN_C1, MT_C3) esta questão avalia.
    
    FORMATO DE RETORNO (JSON APENAS):
    {{
        "explanation": "Explicação pedagógica passo a passo.",
        "subtopics": ["lista", "de", "subtópicos"],
        "difficulty": "Fácil" | "Médio" | "Difícil",
        "is_diagnostic": boolean,
        "skills": ["H1", "H17"],
        "competencies": ["CN_C1", "MT_C3"]
    }}
    Responda APENAS o JSON puro.
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
        
        for q in questions:
            # Verificar se a questão já foi processada (opcional, para economia de tokens)
            result = session.run("MATCH (q:Question {id: $id}) RETURN q.explanation as exp", id=q['id']).single()
            if result and result['exp']:
                print(f"Questão {q['id']} já processada. Pulando...")
                continue

            print(f"Processando questão {q['id']}...")
            
            enrichment = get_enrichment(q['question'], q['choices']['text'])
            if not enrichment:
                continue
            
            # Aqui geraríamos o embedding real. 
            # Por enquanto usaremos um vetor fake ou chamaremos o modelo de embedding do Gemini.
            # O modelo 'text-embedding-004' do Gemini gera 768 dimensões.
            try:
                embedding_response = genai.embed_content(
                    model="models/gemini-embedding-2",
                    content=q['question'] + " " + enrichment['explanation'],
                    task_type="retrieval_document"
                )
                embedding = embedding_response['embedding']
            except Exception as e:
                print(f"Erro no Embedding: {e}")
                embedding = [0.0] * 3072

            # Inserir no Neo4j
            session.execute_write(ingest_tx, q, enrichment, embedding)
            print(f"Questão {q['id']} inserida com sucesso.")
            time.sleep(1) # Rate limit safety

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
