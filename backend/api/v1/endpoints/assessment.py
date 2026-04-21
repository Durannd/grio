from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.question import get_assessment_questions
from schemas.question import Assessment, Question
from schemas.assessment import AssessmentSubmission
from crud.assessment import process_assessment_submission
from core.neo4j import get_driver

router = APIRouter()

from schemas.question import Assessment, Question, Question

@router.get("/assessment", response_model=Assessment)
def read_assessment(db: Session = Depends(get_db)):
    questions = get_assessment_questions(db)
    for q in questions:
        if q.correct_option:
            q.correct_option_id = q.correct_option.id
    return {"questions": questions}

@router.post("/assessment/submit")
def submit_assessment(submission: AssessmentSubmission, db: Session = Depends(get_db)):
    return process_assessment_submission(db, submission)
