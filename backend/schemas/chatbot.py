from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str # "user" or "model"
    content: str = Field(..., min_length=1, max_length=10000)

class MentorRequest(BaseModel):
    question_id: str = Field(..., min_length=1, max_length=100)
    selected_option_id: int = Field(..., ge=0, le=5)  # 0 para modo genérico, 1-5 para específico
    chat_history: List[ChatMessage] = []
    user_message: Optional[str] = None

class MentorResponse(BaseModel):
    response: str
    skill_targeted: Optional[str] = None
    is_correct: bool
