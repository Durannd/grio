from pydantic import BaseModel
from typing import Optional

class MicroLesson(BaseModel):
    skill_id: str
    content: str
    description: str
    area: Optional[str] = None

class StudyRequest(BaseModel):
    skill_id: str
