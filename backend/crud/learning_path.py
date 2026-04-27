from neo4j import Driver

def get_user_learning_path(driver: Driver, user_id: int):
    with driver.session() as session:
        # Busca habilidades onde o usuário tem proficiência, ordenados por score (prioriza o que ele menos sabe)
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s:Skill) "
            "WHERE r.score >= 0 "
            "RETURN s.id AS id, s.description AS description, r.score AS score, COALESCE(r.is_inferred, false) AS is_inferred "
            "ORDER BY r.score ASC",
            user_id=user_id
        )

        path = []
        for record in result:
            path.append({
                "area_id": record["id"][:2] if record["id"] else "MT",
                "concept_name": record["id"], # Usando ID como nome (ex: MT_C1_H1)
                "description": record["description"],
                "score": record["score"],
                "is_inferred": record["is_inferred"]
            })

        if not path:
            return [
                {"area_id": "MT", "concept_name": "Nivelamento: Matemática", "description": "Fundamentos de lógica e aritmética para o ENEM.", "score": 0.0},
                {"area_id": "LC", "concept_name": "Nivelamento: Linguagens", "description": "Estratégias de interpretação de texto e gêneros literários.", "score": 0.0},
                {"area_id": "CH", "concept_name": "Nivelamento: Humanas", "description": "Análise de processos históricos e sociais básicos.", "score": 0.0}
            ]
            
        return path

def get_full_learning_path(driver: Driver, user_id: int):
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Area)<-[:BELONGS_TO]-(c:Competence)<-[:PART_OF]-(s:Skill)
            OPTIONAL MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s)
            RETURN a.name AS area,
                   s.id AS id, 
                   s.description AS description, 
                   COALESCE(r.score, 0.0) AS score, 
                   COALESCE(r.is_inferred, false) AS is_inferred
            ORDER BY a.name, s.id ASC
        """, user_id=user_id)

        path = []
        for record in result:
            path.append({
                "area": record["area"],
                "area_id": record["id"][:2] if record["id"] else "MT",
                "concept_name": record["id"],
                "description": record["description"],
                "score": record["score"],
                "is_inferred": record["is_inferred"]
            })

        return path

