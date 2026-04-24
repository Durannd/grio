import os
from dotenv import load_dotenv
import neo4j
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def ensure_constraints():
    """Garante que o banco tenha as restrições necessárias para evitar duplicatas e ter performance."""
    uri = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    constraints = [
        "CREATE CONSTRAINT area_name IF NOT EXISTS FOR (a:Area) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT subtopic_name IF NOT EXISTS FOR (s:Subtopic) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE q.id IS UNIQUE",
        "CREATE CONSTRAINT comp_id IF NOT EXISTS FOR (c:Competence) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (sk:Skill) REQUIRE sk.id IS UNIQUE",
        "CREATE CONSTRAINT cognitive_axis_id IF NOT EXISTS FOR (e:CognitiveAxis) REQUIRE e.id IS UNIQUE"
    ]
    
    with driver.session() as session:
        print("⚙️ Verificando/Criando restrições de unicidade...", flush=True)
        for cmd in constraints:
            try:
                session.run(cmd)
            except Exception as e:
                print(f"⚠️ Aviso ao criar restrição: {e}", flush=True)
        
        # Índice Vetorial (768 dimensões para text-embedding-004)
        print("⚙️ Verificando índice vetorial...", flush=True)
        try:
            session.run("CREATE VECTOR INDEX question_embeddings IF NOT EXISTS FOR (q:Question) ON (q.embedding) "
                        "OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}")
        except Exception as e:
            print(f"⚠️ Aviso ao criar índice vetorial: {e}", flush=True)

    driver.close()
    print("✅ Banco de dados otimizado e protegido!", flush=True)

if __name__ == "__main__":
    ensure_constraints()
