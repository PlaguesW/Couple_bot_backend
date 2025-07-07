from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class IdeaResponse(IdeaBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True