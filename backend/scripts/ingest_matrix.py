import json
from core.neo4j import get_driver

def ingest_matrix(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    driver = get_driver()
    with driver.session() as session:
        # 1. Ingerir Eixos Cognitivos
        for eixo in data["eixos_cognitivos"]:
            session.run("""
                MERGE (e:CognitiveAxis {id: $id})
                SET e.name = $name, e.description = $description
            """, id=eixo["id"], name=eixo["nome"], description=eixo["descricao"])
        
        # 2. Ingerir Áreas, Competências e Habilidades
        for area in data["areas"]:
            session.run("MERGE (a:Area {name: $name})", name=area["nome"])
            
            for comp in area["competencias"]:
                session.run("""
                    MATCH (a:Area {name: $area_name})
                    MERGE (c:Competence {id: $id})
                    SET c.description = $description
                    MERGE (c)-[:BELONGS_TO]->(a)
                """, area_name=area["nome"], id=comp["id"], description=comp["descricao"])
                
                for skill in comp["habilidades"]:
                    # No Neo4j, habilidades são compartilhadas em IDs (H1, H2...) mas pertencem a competências específicas
                    # Para evitar colisão global de H1, vamos usar ID composto
                    skill_unique_id = f"{comp['id']}_{skill['id']}"
                    session.run("""
                        MATCH (c:Competence {id: $comp_id})
                        MERGE (s:Skill {id: $id})
                        SET s.code = $code, s.description = $description
                        MERGE (s)-[:PART_OF]->(c)
                    """, comp_id=comp["id"], id=skill_unique_id, code=skill["id"], description=skill["descricao"])

    print("Matriz de Referência ingerida no Neo4j!")

if __name__ == "__main__":
    ingest_matrix("scripts/enem_matrix_full.json")
