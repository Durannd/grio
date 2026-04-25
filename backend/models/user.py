from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    avatar_url = Column(String, nullable=True)
    is_diagnostic_completed = Column(Integer, default=0)
    study_plan_cache = Column(String, nullable=True) # Armazena o JSON do plano gerado pela IA
