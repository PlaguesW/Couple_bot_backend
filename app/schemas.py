from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum

class DateStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"

# Users
class UserBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    telegram_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    pass

class User(UserBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# PartnerPair Schemas
class PartnerPairBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    user1_id: str = Field(..., min_length=1, max_length=100)
    user2_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('user2_id')
    def users_must_be_different(cls, v, values):
        if 'user1_id' in values and v == values['user1_id']:
            raise ValueError('user1_id and user2_id must be different')
        return v

class PartnerPairCreate(PartnerPairBase):
    pass

class PartnerPair(PartnerPairBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

# Ideas
class IdeaBase(BaseModel):
    idea_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=2000)

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)

class Idea(IdeaBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

# Date Events
class DateEventBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    pair_id: str = Field(..., min_length=1, max_length=100)
    idea_id: str = Field(..., min_length=1, max_length=100)
    proposer_id: str = Field(..., min_length=1, max_length=100)
    accepted: bool = False
    date_status: DateStatusEnum = DateStatusEnum.pending
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class DateEventCreate(DateEventBase):
    pass

class DateEventUpdate(BaseModel):
    accepted: Optional[bool] = None
    date_status: Optional[DateStatusEnum] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class DateEvent(DateEventBase):
    created_at: datetime
    
    class Config:
        from_attributes = True