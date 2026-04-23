from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class OptionBase(BaseModel):
    text: str

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class QuestionBase(BaseModel):
    text: str
    difficulty: str
    concept_name: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: str
    options: List[Option] = []
    correct_option_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class Assessment(BaseModel):
    questions: List[Question]
