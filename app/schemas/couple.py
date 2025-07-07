from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CoupleBase(BaseModel):
    pass


class CoupleCreate(BaseModel):
    user_id: int


class CoupleJoin(BaseModel):
    user_id: int
    invite_code: str


class CoupleResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: Optional[int] = None
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True