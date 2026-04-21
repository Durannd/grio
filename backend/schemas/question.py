from pydantic import BaseModel
from typing import List

class QuestionBase(BaseModel):
    text: str
    difficulty: str
    concept_name: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True

class Assessment(BaseModel):
    questions: List[Question]
