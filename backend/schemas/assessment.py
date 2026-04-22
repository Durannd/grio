from typing import List
from pydantic import BaseModel

class Answer(BaseModel):
    question_id: int
    selected_option_id: int

class AssessmentSubmission(BaseModel):
    user_id: int
    answers: List[Answer]
