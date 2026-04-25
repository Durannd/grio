from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    type = Column(String, default="diagnostico") # 'diagnostico' or 'simulado'
    
    # Store the snapshot of proficiencies calculated at this point in time
    proficiencies_snapshot = Column(JSON, nullable=True)
    
    # Store the AI generated report for this attempt
    analysis_json = Column(JSON, nullable=True)

    user = relationship("User", backref="assessment_attempts")
