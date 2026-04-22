from fastapi import APIRouter, Depends
from core.neo4j import get_driver
from crud import concept as crud_concept
from schemas import concept as schema_concept

router = APIRouter()

@router.post("/", response_model=schema_concept.Concept)
def create_concept(
    concept: schema_concept.ConceptCreate,
    db_driver=Depends(get_driver)
):
    return crud_concept.create_concept(db_driver, concept)
