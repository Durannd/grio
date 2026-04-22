from pydantic import BaseModel, ConfigDict
from typing import Optional

class ConceptBase(BaseModel):
    name: str
    description: str | None = None

class ConceptCreate(ConceptBase):
    pass

class Concept(ConceptBase):
    id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
