from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas import PartnerPairCreate, PartnerPair
from app.crud import (
    create_pair, 
    get_pair, 
    get_pair_by_user_id,
    generate_pair_code, 
    join_pair,
    get_user
)
from app.database import get_db
from pydantic import BaseModel, ValidationError
import json

router = APIRouter(prefix="/pairs", tags=["Pairs"])

class JoinPairRequest(BaseModel):
    code: str
    user_id: str

@router.post("/", response_model=PartnerPair)
async def create_new_pair(request: Request, db: Session = Depends(get_db)):
    """Создать новую пару с отладкой"""
    try:
        body = await request.body()
        print(f"Raw request body: {body}")
        
        try:
            json_data = json.loads(body)
            print(f"Parsed JSON: {json_data}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        try:
            pair = PartnerPairCreate(**json_data)
            print(f"Created PartnerPairCreate: {pair}")
        except ValidationError as e:
            print(f"Validation error: {e}")
            if 'user1_id' in json_data:
                pair = PartnerPairCreate(user1_id=json_data['user1_id'])
            elif 'user_id' in json_data:
                pair = PartnerPairCreate(user1_id=json_data['user_id'])
            else:
                raise HTTPException(status_code=422, detail=f"Missing required fields: {e}")
        
        user = get_user(db, pair.user1_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_pair = get_pair_by_user_id(db, pair.user1_id)
        if existing_pair:
            raise HTTPException(status_code=400, detail="User already in a pair")
        
        db_pair = create_pair(db, pair)
        return db_pair
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/join", response_model=PartnerPair)
def join_existing_pair(request: JoinPairRequest, db: Session = Depends(get_db)):
    """Присоединиться к паре по коду приглашения"""
    user = get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_pair = get_pair_by_user_id(db, request.user_id)
    if existing_pair:
        raise HTTPException(status_code=400, detail="User already in a pair")
    
    db_pair = join_pair(db, request.code, request.user_id)
    if not db_pair:
        raise HTTPException(status_code=404, detail="Pair not found or invalid code")
    return db_pair

@router.get("/status/{pair_id}", response_model=PartnerPair)
def get_pair_status(pair_id: str, db: Session = Depends(get_db)):
    """Получить статус пары по ID"""
    db_pair = get_pair(db, pair_id)
    if not db_pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    return db_pair

@router.get("/user/{user_id}", response_model=PartnerPair)
def get_user_pair(user_id: str, db: Session = Depends(get_db)):
    """Получить пару пользователя"""
    db_pair = get_pair_by_user_id(db, user_id)
    if not db_pair:
        raise HTTPException(status_code=404, detail="User is not in any pair")
    return db_pair

@router.get("/generate-code")
def generate_pair_invitation_code(db: Session = Depends(get_db)):
    """Генерировать код приглашения"""
    code = generate_pair_code(db)
    return {"code": code}