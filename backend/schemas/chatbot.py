from typing import List, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class MentorRequest(BaseModel):
    question_id: str
    selected_option_id: int
    chat_history: List[ChatMessage] = []

class MentorResponse(BaseModel):
    response: str
    skill_targeted: Optional[str] = None
    is_correct: bool
