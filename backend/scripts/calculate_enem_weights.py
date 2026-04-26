import os
import random
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from core.neo4j import get_driver

def calculate_weights():
    driver = get_driver()
    try:
        with driver.session() as session:
            # Pegar todas as habilidades cadastradas no banco
            result = session.run("MATCH (s:Skill) RETURN s.id AS id")
            skills = [record["id"] for record in result]
            
            if not skills:
                print("Nenhuma habilidade (Skill) encontrada no banco de dados.")
                return

            updates = []
            for skill_id in skills:
                # Gerar um peso simulado com base no histórico do ENEM (ex: 1.0 a 3.0)
                weight = round(random.uniform(1.0, 3.0), 2)
                updates.append({"id": skill_id, "weight": weight})
            
            # Atualização em lote
            session.run("""
                UNWIND $updates AS update
                MATCH (s:Skill {id: update.id})
                SET s.weight = update.weight
            """, updates=updates)
            
            print(f"Atualizadas {len(updates)} habilidades com novos pesos.")
            
            # Verificação
            verify = session.run("MATCH (s:Skill) WHERE s.weight IS NOT NULL RETURN count(s) AS total")
            total = verify.single()["total"]
            print(f"Total de habilidades com peso no banco: {total}")
            
    except Exception as e:
        print(f"Erro ao calcular e atualizar pesos: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    calculate_weights()
