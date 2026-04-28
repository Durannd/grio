from pydantic import BaseModel
from typing import Optional

class MicroLesson(BaseModel):
    skill_id: str
    friendly_name: Optional[str] = None
    content: str
    description: str
    area: Optional[str] = None

class StudyRequest(BaseModel):
    skill_id: str
