import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="backend/.env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def run_diagnostics():
    print(f"Conectando ao Neo4j em: {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    queries = {
        "Total de Questões": "MATCH (q:Question) RETURN count(q) as count",
        "Questões SEM Subtópicos (Soltas)": "MATCH (q:Question) WHERE NOT (q)-[:COVERS_TOPIC]->(:Subtopic) RETURN count(q) as count",
        "Questões COM Subtópicos": "MATCH (q:Question) WHERE (q)-[:COVERS_TOPIC]->(:Subtopic) RETURN count(q) as count",
        "Total de Subtópicos": "MATCH (s:Subtopic) RETURN count(s) as count",
        "Subtópicos SEM Tópico (Pai)": "MATCH (s:Subtopic) WHERE NOT (s)-[:PART_OF]->() AND NOT (s)-[:BELONGS_TO]->() RETURN count(s) as count",
        "Total de Habilidades (Skill)": "MATCH (s:Skill) RETURN count(s) as count",
        "Questões COM Habilidades": "MATCH (q:Question) WHERE (q)-[:REQUIRES_SKILL]->(:Skill) RETURN count(q) as count",
        "Questões COM Competências": "MATCH (q:Question) WHERE (q)-[:REQUIRES_COMPETENCE]->(:Competence) RETURN count(q) as count",
        "Total de Áreas": "MATCH (a:Area) RETURN count(a) as count",
        "Visão Geral de Nós (Labels)": "MATCH (n) RETURN labels(n) as label, count(*) as count"
    }
    
    try:
        with driver.session() as session:
            print("\nRELATORIO DE DIAGNOSTICO DO GRAFO")
            print("="*40)
            for title, query in queries.items():
                result = session.run(query)
                print(f"\n--- {title} ---")
                records = list(result)
                if not records:
                    print("Nenhum resultado encontrado.")
                    continue
                
                for record in records:
                    if len(record) == 1:
                        print(f"Resultado: {record[0]}")
                    else:
                        print(f" {record.data()}")
            print("\n" + "="*40)
            
    except Exception as e:
        print(f"Erro ao executar diagnostico: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    run_diagnostics()
