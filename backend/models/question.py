from sqlalchemy import Column, Integer, String, Enum
from backend.database import Base
import enum

class DifficultyEnum(str, enum.Enum):
    facil = "facil"
    media = "media"
    dificil = "dificil"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    difficulty = Column(Enum(DifficultyEnum))
    concept_name = Column(String, index=True)
