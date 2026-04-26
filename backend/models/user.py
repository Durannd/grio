from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    avatar_url = Column(String, nullable=True)
    is_diagnostic_completed = Column(Boolean, default=False)
    study_plan_cache = Column(String, nullable=True) # Armazena o JSON do plano gerado pela IA
    current_streak = Column(Integer, default=0)
    last_activity_date = Column(String, nullable=True) # YYYY-MM-DD
