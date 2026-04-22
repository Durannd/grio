from neo4j import Driver

def get_user_learning_path(driver: Driver, user_id: int):
    with driver.session() as session:
        # Busca conceitos onde o usuário tem proficiência, ordenados do menor para o maior score
        result = session.run(
            "MATCH (u:User {id: $user_id})-[r:HAS_PROFICIENCY]->(c:Concept) "
            "RETURN c.name AS concept_name, c.description AS description, r.score AS score "
            "ORDER BY r.score ASC",
            user_id=user_id
        )
        
        path = []
        for record in result:
            path.append({
                "concept_name": record["concept_name"],
                "description": record["description"],
                "score": record["score"]
            })
            
        # Se o usuário não tem proficiências (ex: não fez a prova), retorna uma trilha padrão
        if not path:
            return [
                {"concept_name": "Aritmética Básica", "description": "Operações fundamentais: soma, subtração, multiplicação, divisão.", "score": 0.0},
                {"concept_name": "Álgebra Básica", "description": "Introdução a variáveis e equações de 1º grau.", "score": 0.0},
                {"concept_name": "Geometria Plana", "description": "Formas básicas, áreas e perímetros.", "score": 0.0}
            ]
            
        return path
