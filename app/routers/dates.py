from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.date_event import DateEventCreate, DateEventResponse, DateEventUpdate
from app.database import db

router = APIRouter(prefix="/dates", tags=["dates"])


@router.post("/proposal", response_model=DateEventResponse)
async def create_date_proposal(proposal_data: DateEventCreate):
    """Create a date proposal"""
    # Verify that the couple exists
    couple = await db.get_couple_by_id(proposal_data.couple_id)
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple not found"
        )
    
    # Verify that the idea exists
    idea = await db.get_idea_by_id(proposal_data.idea_id)
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Verify that the proposer is part of the couple
    if proposal_data.proposer_id not in [couple['user1_id'], couple['user2_id']]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of this couple"
        )
    
    date_event = await db.create_date_proposal(
        couple_id=proposal_data.couple_id,
        idea_id=proposal_data.idea_id,
        proposer_id=proposal_data.proposer_id
    )
    
    return DateEventResponse(**date_event)


@router.post("/respond", response_model=DateEventResponse)
async def respond_to_date_proposal(event_id: int, response: str):
    """Respond to a date proposal (accept/reject)"""
    if response not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response must be 'accepted' or 'rejected'"
        )
    
    date_event = await db.respond_to_date_proposal(event_id, response)
    if not date_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Date proposal not found or already responded to"
        )
    
    return DateEventResponse(**date_event)


@router.get("/history/{couple_id}", response_model=List[DateEventResponse])
async def get_date_history(couple_id: int, limit: int = 10):
    """Get date history for a couple"""
    # Verify that the couple exists
    couple = await db.get_couple_by_id(couple_id)
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple not found"
        )
    
    history = await db.get_date_history(couple_id, limit)
    return [DateEventResponse(**event) for event in history]


@router.get("/{event_id}", response_model=DateEventResponse)
async def get_date_event(event_id: int):
    """Get specific date event"""
    date_event = await db.get_date_event_by_id(event_id)
    if not date_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Date event not found"
        )
    return DateEventResponse(**date_event)