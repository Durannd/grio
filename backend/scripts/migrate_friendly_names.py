import json
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="backend/.env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível para backend/ e depois entra em core/
JSON_PATH = os.path.join(BASE_DIR, "..", "core", "skill_translations.json")
# Sobe um nível para backend/ e busca o .env
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

def migrate_friendly_names():
    load_dotenv(dotenv_path=ENV_PATH)
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    if not os.path.exists(JSON_PATH):
        print(f"Arquivo {JSON_PATH} não encontrado. Pulando migração.")
        return

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return

    # Ajusta URI para ignorar validação de certificado (+ssc)
    final_uri = NEO4J_URI
    if "+s" in final_uri and "+ssc" not in final_uri:
        final_uri = final_uri.replace("+s", "+ssc")
    elif "bolt://" in final_uri:
        final_uri = final_uri.replace("bolt://", "bolt+ssc://")
    elif "neo4j://" in final_uri:
        final_uri = final_uri.replace("neo4j://", "neo4j+ssc://")

    print(f"Conectando em {final_uri}...")
    driver = GraphDatabase.driver(
        final_uri, 
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        print(f"Iniciando migração de {len(translations)} nomes para o Neo4j...")
        
        counter = 0
        for skill_id, friendly_name in translations.items():
            # MERGE para garantir que a propriedade seja criada/atualizada no nó Skill
            query = """
            MATCH (s:Skill {id: $skill_id})
            SET s.friendly_name = $friendly_name
            RETURN s.id
            """
            result = session.run(query, skill_id=skill_id, friendly_name=friendly_name)
            if result.single():
                counter += 1
        
        print(f"Sucesso! {counter} habilidades foram atualizadas com friendly_name.")

    driver.close()

if __name__ == "__main__":
    migrate_friendly_names()
