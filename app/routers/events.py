from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import DateEventCreate, DateEvent
from app.crud import create_date_event, respond_to_proposal, get_date_history
from app.database import get_db

router = APIRouter(prefix="/date", tags=["Events"])

@router.post("/proposal", response_model=DateEvent)
def propose_date(event: DateEventCreate, db: Session = Depends(get_db)):
    try:
        db_event = create_date_event(db, event)
        return db_event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/respond")
def respond_to_date_proposal(proposal_id: str, accepted: bool, db: Session = Depends(get_db)):
    result = respond_to_proposal(db, proposal_id, accepted)
    if not result:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"detail": "Proposal responded", "event": result}

@router.get("/history")
def get_date_history_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    history = get_date_history(db, skip, limit)
    return history