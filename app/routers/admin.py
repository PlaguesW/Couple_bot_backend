from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import get_all_users, get_all_pairs, get_all_ideas
from app.database import get_db
from app.schemas import User, PartnerPair, Idea

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=list[User])
def read_all_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return users

@router.get("/pairs", response_model=list[PartnerPair])
def read_all_pairs(db: Session = Depends(get_db)):
    pairs = get_all_pairs(db)
    return pairs

@router.get("/ideas", response_model=list[Idea])
def read_all_ideas(db: Session = Depends(get_db)):
    ideas = get_all_ideas(db)
    return ideas