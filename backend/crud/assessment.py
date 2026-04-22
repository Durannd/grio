from sqlalchemy.orm import Session
from backend.schemas.assessment import AssessmentSubmission
from backend.models.question import Question
from backend.core.neo4j import get_driver
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

    # Grava a proficiência no Neo4j
    driver = get_driver()
    with driver.session() as session:
        for concept, total in totals.items():
            score = scores[concept] / total if total > 0 else 0
            session.run(
                "MATCH (u:User {id: $user_id}) "
                "MERGE (c:Concept {name: $concept}) "
                "MERGE (u)-[r:HAS_PROFICIENCY]->(c) "
                "SET r.score = $score",
                user_id=submission.user_id,
                concept=concept,
                score=score
            )

    return {"status": "success", "message": "Assessment submitted successfully."}
