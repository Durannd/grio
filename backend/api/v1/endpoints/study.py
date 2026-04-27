from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.neo4j import get_driver
from core.deps import get_current_user
from models.user import User
from crud.study import get_or_generate_microlesson
from crud.user import update_user_streak
from schemas.study import MicroLesson
from core.translator import get_friendly_name, unmask_id

router = APIRouter()

@router.get("/{skill_id}", response_model=MicroLesson)
def read_microlesson(
    skill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Desmascara o ID se ele vier no formato SKL-
    actual_skill_id = unmask_id(skill_id)
    driver = get_driver()
    update_user_streak(db, current_user)
    lesson = get_or_generate_microlesson(driver, actual_skill_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Habilidade não encontrada")
    return lesson
