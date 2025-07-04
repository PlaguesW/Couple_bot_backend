from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from models import ProposalStatus

#* Users


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#* Pairs


class PairBase(BaseModel):
    name: Optional[str] = None


class PairCreate(PairBase):
    creator_telegram_id: int


class PairJoin(BaseModel):
    code: str
    telegram_id: int


class PairResponse(PairBase):
    id: int
    code: str
    user1_telegram_id: int
    user2_telegram_id: Optional[int] = None
    is_complete: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#* Ideas


class IdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(...,
                          pattern="^(romantic|home|cultural|active|budget)$")
    duration: Optional[str] = None
    cost_level: str = Field(..., pattern="^(free|low|medium|high)$")


class IdeaCreate(IdeaBase):
    is_active: bool = True


class IdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(
        None, pattern="^(romantic|home|cultural|active|budget)$")
    duration: Optional[str] = None
    cost_level: Optional[str] = Field(None, pattern="^(free|low|medium|high)$")
    is_active: Optional[bool] = None


class IdeaResponse(IdeaBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#* Dates


class DateProposalBase(BaseModel):
    custom_description: Optional[str] = None
    proposed_date: Optional[date] = None
    proposed_time: Optional[time] = None


class DateProposalCreate(DateProposalBase):
    pair_id: int
    proposer_telegram_id: int
    idea_id: Optional[int] = None


class DateProposalUpdate(BaseModel):
    status: ProposalStatus
    responder_telegram_id: int
    response_note: Optional[str] = None


class DateProposalResponse(DateProposalBase):
    id: int
    pair_id: int
    proposer_telegram_id: int
    responder_telegram_id: Optional[int] = None
    idea_id: Optional[int] = None
    status: ProposalStatus
    response_note: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None

    idea: Optional[IdeaResponse] = None

    class Config:
        from_attributes = True

# * Statustics


class PairStatsResponse(BaseModel):
    pair_id: int
    total_proposals: int
    accepted_proposals: int
    rejected_proposals: int
    pending_proposals: int
    acceptance_rate: float


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
