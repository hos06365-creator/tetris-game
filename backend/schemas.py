from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    high_score: int

    model_config = {"from_attributes": True}


class AuthResponse(Token):
    user: UserRead


class ScoreCreate(BaseModel):
    score: int = Field(ge=0)
    lines: int = Field(default=0, ge=0)


class ScoreRead(BaseModel):
    id: int
    score: int
    lines: int
    created_at: datetime

    model_config = {"from_attributes": True}


class GlobalHighScore(BaseModel):
    score: int
    email: EmailStr | None = None


class ScoreSaveResponse(BaseModel):
    score: ScoreRead
    user_high_score: int
    global_high_score: GlobalHighScore
