import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def clear_nature():
    # Ajuste para Neo4j Aura (ssc)
    uri = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        print("--- Limpando dados incompletos de 'Ciencias da Natureza e suas Tecnologias'...")
        
        # 1. Deletar questões vinculadas à essa área
        query = """
        MATCH (a:Area {name: 'Ciências da Natureza e suas Tecnologias'})<-[:BELONGS_TO]-(t:Topic)<-[:PART_OF]-(s:Subtopic)<-[:COVERS_TOPIC]-(q:Question)
        DETACH DELETE q
        """
        session.run(query)
        print("OK: Questoes de Natureza removidas.")

        # 2. Remover a área, tópicos e subtópicos
        query_meta = """
        MATCH (a:Area {name: 'Ciências da Natureza e suas Tecnologias'})
        OPTIONAL MATCH (a)<-[:BELONGS_TO]-(t:Topic)
        OPTIONAL MATCH (t)<-[:PART_OF]-(s:Subtopic)
        DETACH DELETE a, t, s
        """
        session.run(query_meta)
        print("OK: Estrutura de metadados de Natureza removida.")
        
        # 3. Remover competências e habilidades órfãs
        query_orphans = """
        MATCH (c:Competence) WHERE c.id STARTS WITH 'CN_' DETACH DELETE c
        """
        session.run(query_orphans)
        query_skill_orphans = """
        MATCH (sk:Skill) WHERE sk.id STARTS WITH 'CN_' DETACH DELETE sk
        """
        session.run(query_skill_orphans)
        print("OK: Competencias e Habilidades de Natureza removidas.")

    driver.close()
    print("\nPronto! Agora você pode rodar o 'Run Ingestion' no GitHub novamente.")

if __name__ == "__main__":
    clear_nature()
