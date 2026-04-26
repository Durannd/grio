from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str
    name: str
    avatar_url: str | None = None
    is_diagnostic_completed: int = 0

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    current_streak: int = 0
    last_activity_date: str | None = None

    model_config = ConfigDict(from_attributes=True)

