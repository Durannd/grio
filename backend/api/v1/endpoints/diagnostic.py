from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session as Neo4jSession
from core.connections import get_neo4j_session
from infrastructure.repositories.diagnostic_repository import Neo4jDiagnosticRepository
from domain.services.root_cause_service import RootCauseService
from core.deps import get_current_user
from models.user import User

router = APIRouter()

def get_root_cause_service(neo4j_session: Neo4jSession = Depends(get_neo4j_session)):
    repo = Neo4jDiagnosticRepository(neo4j_session)
    return RootCauseService(repo)

@router.get("/{student_id}/root-cause")
def get_root_cause(
    student_id: str,
    question_id: str,
    service: RootCauseService = Depends(get_root_cause_service),
    current_user: User = Depends(get_current_user)
):
    if not question_id:
        raise HTTPException(status_code=400, detail="question_id is required")
    
    # Ensure user can only query their own root causes
    if str(current_user.id) != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
        
    result = service.analyze_failure(student_id, question_id)
    return result
