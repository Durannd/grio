from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class OptionBase(BaseModel):
    text: str

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    text: str
    difficulty: str
    concept_name: str

class QuestionCreate(QuestionBase):
    pass

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class OptionBase(BaseModel):
    text: str

class OptionCreate(OptionBase):
    pass

class Option(OptionBase):
    id: int

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    text: str
    difficulty: str
    concept_name: str

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    options: List[Option] = []
    correct_option_id: Optional[int] = None

    class Config:
        orm_mode = True


    class Config:
        orm_mode = True

class Assessment(BaseModel):
    questions: List[Question]

class Assessment(BaseModel):
    questions: List[Question]
