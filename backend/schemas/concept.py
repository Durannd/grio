from pydantic import BaseModel

class ConceptBase(BaseModel):
    name: str
    description: str | None = None

class ConceptCreate(ConceptBase):
    pass

class Concept(ConceptBase):
    id: int

    class Config:
        orm_mode = True
