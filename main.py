from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
import secrets
import string

from database import get_db, engine
from models import Base, User, Pair, Idea, DateProposal, ProposalStatus
from schemas import (
    UserCreate, UserResponse, UserUpdate,
    PairCreate, PairResponse, PairJoin,
    IdeaCreate, IdeaResponse,
    DateProposalCreate, DateProposalResponse, DateProposalUpdate
)
from config import settings

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Couple Bot API",
    description="API для бота знакомств и планирования свиданий",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверка токена API"""
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )
    return credentials.credentials

def generate_pair_code() -> str:
    """Генерация кода для пары"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

#* User Endpoints

@app.post("/api/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Создание нового пользователя"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == user.telegram_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    db_user = User(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение пользователя по telegram_id"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{telegram_id}", response_model=UserResponse)
async def update_user(telegram_id: int, user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Обновление данных пользователя"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{telegram_id}")
async def delete_user(telegram_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Удаление пользователя"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

#* endpoint for User

@app.post("/api/pairs/", response_model=PairResponse)
async def create_pair(pair: PairCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Создание новой пары"""
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == pair.creator_telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already in a pair
    existing_pair = db.query(Pair).filter(
        (Pair.user1_telegram_id == pair.creator_telegram_id) | 
        (Pair.user2_telegram_id == pair.creator_telegram_id)
    ).first()
    if existing_pair:
        raise HTTPException(status_code=400, detail="User already in a pair")
    
    # Generate unique pair code
    code = generate_pair_code()
    while db.query(Pair).filter(Pair.code == code).first():
        code = generate_pair_code()
    
    db_pair = Pair(
        code=code,
        user1_telegram_id=pair.creator_telegram_id,
        name=pair.name
    )
    db.add(db_pair)
    db.commit()
    db.refresh(db_pair)
    return db_pair

@app.post("/api/pairs/join", response_model=PairResponse)
async def join_pair(pair_join: PairJoin, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Присоединение к паре по коду"""
    # Get the pair by code
    pair = db.query(Pair).filter(Pair.code == pair_join.code).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    
    # Check if pair.is_complete
    if pair.user2_telegram_id:
        raise HTTPException(status_code=400, detail="Pair is already full")
    
    # Check pair dublicate
    if pair.user1_telegram_id == pair_join.telegram_id:
        raise HTTPException(status_code=400, detail="Cannot join your own pair")
    
    # Check existing user
    user = db.query(User).filter(User.telegram_id == pair_join.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check other user pairs if exist
    existing_pair = db.query(Pair).filter(
        (Pair.user1_telegram_id == pair_join.telegram_id) | 
        (Pair.user2_telegram_id == pair_join.telegram_id)
    ).first()
    if existing_pair:
        raise HTTPException(status_code=400, detail="User already in a pair")
    
    # Connect to pair
    pair.user2_telegram_id = pair_join.telegram_id
    pair.is_complete = True
    db.commit()
    db.refresh(pair)
    return pair

@app.get("/api/pairs/{pair_id}", response_model=PairResponse)
async def get_pair(pair_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение пары по ID"""
    pair = db.query(Pair).filter(Pair.id == pair_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    return pair

@app.get("/api/users/{telegram_id}/pair", response_model=Optional[PairResponse])
async def get_user_pair(telegram_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение пары пользователя"""
    pair = db.query(Pair).filter(
        (Pair.user1_telegram_id == telegram_id) | 
        (Pair.user2_telegram_id == telegram_id)
    ).first()
    return pair

@app.delete("/api/pairs/{pair_id}")
async def delete_pair(pair_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Удаление пары"""
    pair = db.query(Pair).filter(Pair.id == pair_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    
    db.delete(pair)
    db.commit()
    return {"message": "Pair deleted successfully"}

#* Idea endpoints

@app.post("/api/ideas/", response_model=IdeaResponse)
async def create_idea(idea: IdeaCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Создание новой идеи для свидания"""
    db_idea = Idea(
        title=idea.title,
        description=idea.description,
        category=idea.category,
        duration=idea.duration,
        cost_level=idea.cost_level,
        is_active=idea.is_active
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

@app.get("/api/ideas/", response_model=List[IdeaResponse])
async def get_ideas(
    category: Optional[str] = None,
    cost_level: Optional[str] = None,
    active_only: bool = True,
    limit: int = 10,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Получение списка идей с фильтрацией"""
    query = db.query(Idea)
    
    if active_only:
        query = query.filter(Idea.is_active == True)
    
    if category:
        query = query.filter(Idea.category == category)
    
    if cost_level:
        query = query.filter(Idea.cost_level == cost_level)
    
    ideas = query.limit(limit).all()
    return ideas

@app.get("/api/ideas/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение идеи по ID"""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@app.get("/api/ideas/random", response_model=IdeaResponse)
async def get_random_idea(
    category: Optional[str] = None,
    cost_level: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Получение случайной идеи"""
    from sqlalchemy import func
    
    query = db.query(Idea).filter(Idea.is_active == True)
    
    if category:
        query = query.filter(Idea.category == category)
    
    if cost_level:
        query = query.filter(Idea.cost_level == cost_level)
    
    idea = query.order_by(func.random()).first()
    if not idea:
        raise HTTPException(status_code=404, detail="No ideas found")
    return idea

#* Date proposal endpoints

@app.post("/api/proposals/", response_model=DateProposalResponse)
async def create_proposal(proposal: DateProposalCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Создание предложения свидания"""
    pair = db.query(Pair).filter(Pair.id == proposal.pair_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    
    if proposal.proposer_telegram_id not in [pair.user1_telegram_id, pair.user2_telegram_id]:
        raise HTTPException(status_code=403, detail="User not in this pair")
    
    if proposal.idea_id:
        idea = db.query(Idea).filter(Idea.id == proposal.idea_id).first()
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
    
    db_proposal = DateProposal(
        pair_id=proposal.pair_id,
        proposer_telegram_id=proposal.proposer_telegram_id,
        idea_id=proposal.idea_id,
        custom_description=proposal.custom_description,
        proposed_date=proposal.proposed_date,
        proposed_time=proposal.proposed_time,
        status=ProposalStatus.PENDING
    )
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

@app.get("/api/proposals/pair/{pair_id}", response_model=List[DateProposalResponse])
async def get_pair_proposals(
    pair_id: int,
    status: Optional[ProposalStatus] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Получение предложений свиданий для пары"""
    query = db.query(DateProposal).filter(DateProposal.pair_id == pair_id)
    
    if status:
        query = query.filter(DateProposal.status == status)
    
    proposals = query.order_by(DateProposal.created_at.desc()).limit(limit).all()
    return proposals

@app.put("/api/proposals/{proposal_id}", response_model=DateProposalResponse)
async def update_proposal(
    proposal_id: int,
    proposal_update: DateProposalUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Обновление предложения свидания (принятие/отклонение)"""
    proposal = db.query(DateProposal).filter(DateProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    pair = db.query(Pair).filter(Pair.id == proposal.pair_id).first()
    if proposal_update.responder_telegram_id not in [pair.user1_telegram_id, pair.user2_telegram_id]:
        raise HTTPException(status_code=403, detail="User not in this pair")
    
    if proposal.proposer_telegram_id == proposal_update.responder_telegram_id:
        raise HTTPException(status_code=400, detail="Cannot respond to your own proposal")
    
    proposal.status = proposal_update.status
    proposal.responder_telegram_id = proposal_update.responder_telegram_id
    proposal.response_note = proposal_update.response_note
    proposal.responded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(proposal)
    return proposal

@app.get("/api/proposals/{proposal_id}", response_model=DateProposalResponse)
async def get_proposal(proposal_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение предложения по ID"""
    proposal = db.query(DateProposal).filter(DateProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal

#* Statistics endpoints

@app.get("/api/pairs/{pair_id}/stats")
async def get_pair_stats(pair_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Получение статистики пары"""
    pair = db.query(Pair).filter(Pair.id == pair_id).first()
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    
    total_proposals = db.query(DateProposal).filter(DateProposal.pair_id == pair_id).count()
    accepted_proposals = db.query(DateProposal).filter(
        DateProposal.pair_id == pair_id,
        DateProposal.status == ProposalStatus.ACCEPTED
    ).count()
    rejected_proposals = db.query(DateProposal).filter(
        DateProposal.pair_id == pair_id,
        DateProposal.status == ProposalStatus.REJECTED
    ).count()
    pending_proposals = db.query(DateProposal).filter(
        DateProposal.pair_id == pair_id,
        DateProposal.status == ProposalStatus.PENDING
    ).count()
    
    return {
        "pair_id": pair_id,
        "total_proposals": total_proposals,
        "accepted_proposals": accepted_proposals,
        "rejected_proposals": rejected_proposals,
        "pending_proposals": pending_proposals,
        "acceptance_rate": round(accepted_proposals / total_proposals * 100, 2) if total_proposals > 0 else 0
    }

#* Health Check

@app.get("/api/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)