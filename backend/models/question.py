from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
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

    options = relationship("Option", back_populates="question", foreign_keys='Option.question_id', lazy="joined")

    correct_option_id = Column(Integer, ForeignKey("options.id", use_alter=True), nullable=True)
    correct_option = relationship("Option", foreign_keys=[correct_option_id], lazy="joined")

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))

    question = relationship("Question", back_populates="options", foreign_keys=[question_id])
