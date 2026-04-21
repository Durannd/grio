from neo4j import Driver
from schemas.concept import ConceptCreate

def create_concept(driver: Driver, concept: ConceptCreate):
    with driver.session() as session:
        result = session.write_transaction(_create_concept_node, concept)
        return result

def _create_concept_node(tx, concept: ConceptCreate):
    query = (
        "CREATE (c:Concept {name: $name, description: $description}) "
        "RETURN c"
    )
    result = tx.run(query, name=concept.name, description=concept.description)
    return result.single()[0]
