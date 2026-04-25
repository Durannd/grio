import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Carregar variáveis de ambiente
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

uri = NEO4J_URI.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_validation():
    print("🔍 Iniciando Auditoria de Integridade do Grafo...\n")
    
    with driver.session() as session:
        # 1. Total de Questões vs Órfãs
        q_stats = session.run("""
            MATCH (q:Question)
            OPTIONAL MATCH (q)-[r1:REQUIRES_COMPETENCE]->()
            OPTIONAL MATCH (q)-[r2:EVALUATES]->()
            RETURN count(q) as total,
                   count(DISTINCT CASE WHEN r1 IS NULL OR r2 IS NULL THEN q.id END) as orphans
        """).single()
        
        total = q_stats["total"]
        orphans = q_stats["orphans"]
        status_orphans = "✅ OK" if orphans == 0 else f"❌ FALHA ({orphans} questões sem vínculo)"
        print(f"1. Cobertura de Questões: Total {total} | Órfãs {orphans} -> {status_orphans}")

        # 2. Saúde das Áreas
        area_stats = session.run("""
            MATCH (a:Area)
            OPTIONAL MATCH (a)<-[:BELONGS_TO]-(c:Competence)
            RETURN a.name as name, count(c) as comps
        """)
        print("\n2. Estrutura de Áreas:")
        for record in area_stats:
            icon = "✅" if record["comps"] > 0 else "❌"
            print(f"   {icon} {record['name']}: {record['comps']} competências")

        # 3. Densidade de Subtópicos
        sub_stats = session.run("""
            MATCH (s:Subtopic) RETURN count(s) as total
        """).single()
        print(f"\n3. Densidade Taxonômica: {sub_stats['total']} subtópicos únicos.")
        if sub_stats['total'] > 1000:
            print("   ⚠️ Alerta: Volume alto de subtópicos. Pode haver redundância.")
        else:
            print("   ✅ Volume saudável.")

        # 4. Índice Vetorial
        idx_stats = session.run("""
            SHOW INDEXES YIELD name, state, type
            WHERE name = 'question_embeddings'
            RETURN state, type
        """).single()
        if idx_stats:
            print(f"\n4. Busca Semântica: {idx_stats['type']} index está {idx_stats['state']} -> ✅ OK")
        else:
            print("\n4. Busca Semântica: Índice não encontrado -> ❌ FALHA")

    print("\n--- Auditoria Finalizada ---")

if __name__ == "__main__":
    run_validation()
    driver.close()
