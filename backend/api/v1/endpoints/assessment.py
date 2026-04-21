from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.crud.question import get_assessment_questions
from backend.schemas.question import Assessment

router = APIRouter()

@router.get("/assessment", response_model=Assessment)
def read_assessment(db: Session = Depends(get_db)):
    questions = get_assessment_questions(db)
    return {"questions": questions}
