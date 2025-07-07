from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DateEventBase(BaseModel):
    couple_id: int
    idea_id: int
    proposer_id: int


class DateEventCreate(DateEventBase):
    pass


class DateEventResponse(BaseModel):
    id: int
    couple_id: int
    idea_id: int
    proposer_id: int
    date_status: str
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    created_at: datetime
    idea_title: Optional[str] = None
    idea_description: Optional[str] = None
    proposer_name: Optional[str] = None

    class Config:
        from_attributes = True


class DateEventUpdate(BaseModel):
    date_status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None