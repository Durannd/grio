from infrastructure.repositories.diagnostic_repository import Neo4jDiagnosticRepository
from core.translator import mask_id

class RootCauseService:
    def __init__(self, repository: Neo4jDiagnosticRepository):
        self.repository = repository

    def analyze_failure(self, student_id: str, question_id: str):
        causes = self.repository.find_root_cause(student_id, question_id)
        
        # Mascarar IDs para o frontend
        masked_causes = []
        for cause in causes:
            c_copy = cause.copy()
            c_copy["id"] = mask_id(cause["id"])
            masked_causes.append(c_copy)
            
        return {
            "question_id": question_id,
            "student_id": student_id,
            "root_causes": masked_causes
        }
