from typing import List
from pydantic import BaseModel

class Answer(BaseModel):
    question_id: str
    selected_option_id: int
    time_seconds: int = 0

class AssessmentSubmission(BaseModel):
    user_id: int
    answers: List[Answer]
