from fastapi import APIRouter, Depends
from backend.core.neo4j import driver
from backend.crud import concept as crud_concept
from backend.schemas import concept as schema_concept

router = APIRouter()

@router.post("/", response_model=schema_concept.Concept)
def create_concept(
    concept: schema_concept.ConceptCreate,
    db_driver=Depends(lambda: driver)
):
    return crud_concept.create_concept(db_driver, concept)
