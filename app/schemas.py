from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# * Users


class UserBase(BaseModel):
    user_id: str
    telegram_id: int
    name: str
    username: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# * PartnerPair Schemas
class PartnerPairBase(BaseModel):
    id: str
    user1_id: str
    user2_id: str


class PartnerPairCreate(PartnerPairBase):
    pass


class PartnerPair(PartnerPairBase):
    created_at: datetime

    class Config:
        from_attributes = True


# * Ideas
class IdeaBase(BaseModel):
    idea_id: str
    title: str
    description: str


class IdeaCreate(IdeaBase):
    pass


class Idea(IdeaBase):
    created_at: datetime

    class Config:
        from_attributes = True


# * Date Enents
class DateEventBase(BaseModel):
    id: str
    pair_id: str
    idea_id: str
    proposer_id: str
    accepted: bool
    date_status: str  # pending, accepted, completed, cancelled
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None


class DateEventCreate(DateEventBase):
    pass


class DateEvent(DateEventBase):
    created_at: datetime

    class Config:
        from_attributes = True
