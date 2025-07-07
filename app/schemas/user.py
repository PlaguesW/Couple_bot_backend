from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    username: Optional[str] = None


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    telegram_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True