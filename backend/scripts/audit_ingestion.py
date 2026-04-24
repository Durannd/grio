import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def run_audit(json_path):
    print(f"🧐 Iniciando Auditoria Griô...")
    
    # 1. Ler IDs do JSON local
    with open(json_path, "r", encoding="utf-8") as f:
        local_questions = json.load(f)
    local_ids = set(q['id'] for q in local_questions)
    total_local = len(local_ids)
    
    # 2. Ler IDs do Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    db_ids = set()
    
    try:
        with driver.session() as session:
            result = session.run("MATCH (q:Question) RETURN q.id as id")
            for record in result:
                db_ids.add(record['id'])
    finally:
        driver.close()
    
    total_db = len(db_ids)
    
    # 3. Comparar
    missing_ids = local_ids - db_ids
    
    print("\n" + "="*30)
    print(f"📊 RELATÓRIO DE INTEGRIDADE")
    print("="*30)
    print(f"✅ No JSON local: {total_local}")
    print(f"✅ No Neo4j Cloud: {total_db}")
    print(f"❌ Questões Faltantes: {len(missing_ids)}")
    print("="*30)
    
    if missing_ids:
        log_path = "scripts/failed_ingestions.log"
        with open(log_path, "w") as f:
            f.write("\n".join(map(str, sorted(list(missing_ids)))))
        print(f"\n⚠️ IDs faltantes salvos em: {log_path}")
        print(f"💡 Dica: Basta rodar o script de ingestão novamente. Ele vai detectar que esses IDs não existem e processá-los.")
    else:
        print("\n🏆 SUCESSO TOTAL: Todas as questões foram ingeridas corretamente!")

if __name__ == "__main__":
    run_audit("scripts/enem_sample.json")
