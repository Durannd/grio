from neo4j import Session

class Neo4jDiagnosticRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_root_cause(self, student_id: str, question_id: str):
        query = """
        MATCH (s:User {id: $studentId})-[:FAILED]->(q:Question {id: $questionId})-[:REQUIRES]->(c:Concept)
        MATCH p=(c)-[:DEPENDS_ON*0..3]->(pre:Concept)
        OPTIONAL MATCH (s)-[m:MASTERS]->(pre)
        WITH pre, coalesce(m.score, 0.0) AS mastery, length(p) AS dist
        ORDER BY mastery ASC, dist DESC
        RETURN pre.id AS id, pre.name AS name, mastery, dist AS distance
        LIMIT 3
        """
        # Note: Depending on the graph model, the user label might be 'Student' or 'User'. 
        # Using 'User' to match the existing codebase which references User.
        result = self.session.run(query, studentId=student_id, questionId=question_id)
        
        causes = []
        for record in result:
            causes.append({
                "id": record["id"],
                "name": record["name"],
                "mastery": record["mastery"],
                "distance": record["distance"]
            })
        return causes
