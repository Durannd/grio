"""
Safe Delete: Limpa microaulas cacheadas para forçar regeneração via LLM.

Uso:
    python scripts/reset_microlessons.py          # Mostra preview (dry-run)
    python scripts/reset_microlessons.py --execute # Executa o reset

Isso NÃO deleta Skills, proficiências ou questões.
Apenas limpa: content, friendly_name, last_enriched_at
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from neo4j import GraphDatabase

def reset_microlessons(execute: bool = False):
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # 1. Preview: mostrar o que será afetado
        preview = session.run("""
            MATCH (s:Skill)
            WHERE s.content IS NOT NULL OR s.friendly_name IS NOT NULL
            RETURN s.id AS id, 
                   s.friendly_name AS friendly_name,
                   s.last_enriched_at AS last_enriched_at,
                   CASE WHEN s.content IS NOT NULL THEN size(s.content) ELSE 0 END AS content_length
            ORDER BY s.id
        """)

        records = list(preview)
        
        if not records:
            print("✅ Nenhuma microaula cacheada encontrada. Nada a limpar.")
            driver.close()
            return

        print(f"\n📋 {len(records)} skills com microaulas cacheadas:\n")
        print(f"{'ID':<20} {'Friendly Name':<30} {'Content Size':<15} {'Last Updated'}")
        print("-" * 90)
        
        for r in records:
            print(f"{r['id']:<20} {str(r['friendly_name'] or 'null'):<30} {r['content_length']:<15} {r['last_enriched_at'] or 'never'}")

        if not execute:
            print(f"\n⚠️  DRY RUN: Nenhuma alteração feita.")
            print(f"   Para executar o reset, rode: python scripts/reset_microlessons.py --execute\n")
            driver.close()
            return

        # 2. Executar o reset
        result = session.run("""
            MATCH (s:Skill)
            WHERE s.content IS NOT NULL OR s.friendly_name IS NOT NULL
            SET s.content = null,
                s.friendly_name = null,
                s.last_enriched_at = null
            RETURN count(s) AS affected
        """)

        affected = result.single()["affected"]
        print(f"\n✅ Reset concluído! {affected} skills tiveram suas microaulas limpas.")
        print(f"   As microaulas serão regeneradas sob demanda quando o aluno clicar em 'Estudar Este Conceito'.\n")

    driver.close()


if __name__ == "__main__":
    execute_flag = "--execute" in sys.argv
    reset_microlessons(execute=execute_flag)
