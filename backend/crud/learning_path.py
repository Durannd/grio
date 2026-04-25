from neo4j import Driver

def get_user_learning_path(driver: Driver, user_id: int):
    with driver.session() as session:
        # Busca habilidades onde o usuário tem proficiência (> 0), ordenados por score (prioriza o que ele menos sabe)
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(s:Skill) "
            "WHERE r.score > 0 "
            "RETURN s.id AS id, s.description AS description, r.score AS score "
            "ORDER BY r.score ASC",
            user_id=user_id
        )

        path = []
        for record in result:
            path.append({
                "concept_name": record["id"], # Usando ID como nome (ex: MT_C1_H1)
                "description": record["description"],
                "score": record["score"]
            })

        if not path:
            return [
                {"concept_name": "Nivelamento: Matemática", "description": "Fundamentos de lógica e aritmética para o ENEM.", "score": 0.0},
                {"concept_name": "Nivelamento: Linguagens", "description": "Estratégias de interpretação de texto e gêneros literários.", "score": 0.0},
                {"concept_name": "Nivelamento: Humanas", "description": "Análise de processos históricos e sociais básicos.", "score": 0.0}
            ]
            
        return path
