from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import PartnerPairCreate, PartnerPair
from app.crud import create_pair, get_pair, generate_pair_code, join_pair
from app.database import get_db

router = APIRouter(prefix="/pairs", tags=["Pairs"])

@router.post("/", response_model=PartnerPair)
def create_new_pair(pair: PartnerPairCreate, db: Session = Depends(get_db)):
    db_pair = create_pair(db, pair)
    return db_pair

@router.post("/join", response_model=PartnerPair)
def join_existing_pair(code: str, db: Session = Depends(get_db)):
    db_pair = join_pair(db, code)
    if not db_pair:
        raise HTTPException(status_code=404, detail="Pair not found or invalid code")
    return db_pair

@router.get("/status", response_model=PartnerPair)
def get_pair_status(pair_id: str, db: Session = Depends(get_db)):
    db_pair = get_pair(db, pair_id)
    if not db_pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    return db_pair

@router.get("/generate-code", response_model=str)
def generate_pair_invitation_code(db: Session = Depends(get_db)):
    code = generate_pair_code(db)
    return code