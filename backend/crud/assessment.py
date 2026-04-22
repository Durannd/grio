from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from models.question import Question
from core.neo4j import get_driver
from collections import defaultdict

def process_assessment_submission(db: Session, submission: AssessmentSubmission):
    # Dicionários para armazenar pontuações e totais por conceito
    scores = defaultdict(int)
    totals = defaultdict(int)

    # Itera sobre as respostas para calcular a pontuação
    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if question:
            concept = question.concept_name
            totals[concept] += 1
            if question.correct_option_id == answer.selected_option_id:
                scores[concept] += 1

    # Grava a proficiência no Neo4j usando atualização em lote (UNWIND)
    driver = get_driver()
    with driver.session() as session:
        proficiencies_data = []
        for concept, total in totals.items():
            score = scores[concept] / total if total > 0 else 0
            proficiencies_data.append({"concept": concept, "score": score})
        
        if proficiencies_data:
            session.run(
                "MERGE (u:User {id: $user_id}) "
                "WITH u "
                "UNWIND $proficiencies AS prof "
                "MERGE (c:Concept {name: prof.concept}) "
                "MERGE (u)-[r:HAS_PROFICIENCY]->(c) "
                "SET r.score = prof.score",
                user_id=submission.user_id,
                proficiencies=proficiencies_data
            )

    return {"status": "success", "message": "Assessment submitted successfully."}
