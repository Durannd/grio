from fastapi import APIRouter, Depends
from core.neo4j import get_driver
from crud import concept as crud_concept
from schemas import concept as schema_concept
from core.deps import get_current_user
from models.user import User

router = APIRouter()

@router.post("/", response_model=schema_concept.Concept)
def create_concept(
    concept: schema_concept.ConceptCreate,
    db_driver=Depends(get_driver),
    current_user: User = Depends(get_current_user)
):
    return crud_concept.create_concept(db_driver, concept)
