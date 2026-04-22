from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.question import get_assessment_questions
from schemas.question import Assessment, Question
from schemas.assessment import AssessmentSubmission
from crud.assessment import process_assessment_submission
from core.neo4j import get_driver

router = APIRouter()

from schemas.question import Assessment, Question
from core.deps import get_current_user
from models.user import User

@router.get("/", response_model=Assessment)
def read_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    questions = get_assessment_questions(db)
    for q in questions:
        if q.correct_option:
            q.correct_option_id = q.correct_option.id
    return {"questions": questions}

@router.post("/submit")
def submit_assessment(
    submission: AssessmentSubmission, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Overwrite the user_id from the token to ensure security
    submission.user_id = current_user.id
    return process_assessment_submission(db, submission)
