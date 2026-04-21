from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from models.question import Question
from core.neo4j import get_driver

def process_assessment_submission(db: Session, submission: AssessmentSubmission):
    score_by_concept = {}
    total_by_concept = {}

    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            continue

        concept = question.concept_name
        total_by_concept.setdefault(concept, 0)
        total_by_concept[concept] += 1
        score_by_concept.setdefault(concept, 0)

        if answer.selected_option_id == question.correct_option_id:
            score_by_concept[concept] += 1

    driver = get_driver()
    with driver.session() as session:
        for concept, score in score_by_concept.items():
            total = total_by_concept[concept]
            proficiency = score / total if total > 0 else 0
            session.run(
                """
                MATCH (u:User {id: $user_id})
                MERGE (c:Concept {name: $concept_name})
                MERGE (u)-[r:HAS_PROFICIENCY]->(c)
                SET r.score = $score
                """,
                user_id=submission.user_id,
                concept_name=concept,
                score=proficiency,
            )

    return {"status": "success"}
