from sqlalchemy.orm import Session
from app.models import User, PartnerPair, Idea, DateEvent
from app.schemas import UserCreate, PartnerPairCreate, IdeaCreate, DateEventCreate
from fastapi import HTTPException
from app.models import User as UserModel
import uuid
import random
import string

# User
def create_user(db: Session, user: UserCreate):
    existing_user = db.query(User).filter(User.user_id == user.user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail=f"User with ID {user.user_id} already exists"
        )
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str):
    print(f"CRUD: Searching for user_id: {user_id}")
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    print(f"CRUD: Found user: {user}")
    return user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_users_count(db: Session):
    return db.query(User).count()

# def get_user_by_telegram_id(db: Session, telegram_id: int):
#     return db.query(User).filter(User.telegram_id == telegram_id).first()

#* Pairs
def create_pair(db: Session, pair: PartnerPairCreate):
    pair_id = str(uuid.uuid4())
    
    invitation_code = generate_invitation_code()
    
    db_pair = PartnerPair(
        id=pair_id,
        user1_id=pair.user1_id,
        user2_id=pair.user2_id,
        invitation_code=invitation_code
    )
    
    db.add(db_pair)
    db.commit()
    db.refresh(db_pair)
    return db_pair

def get_pair(db: Session, pair_id: str):
    return db.query(PartnerPair).filter(PartnerPair.id == pair_id).first()

def get_pair_by_user_id(db: Session, user_id: str):
    """Получить пару по ID пользователя"""
    return db.query(PartnerPair).filter(
        (PartnerPair.user1_id == user_id) | 
        (PartnerPair.user2_id == user_id)
    ).first()

def generate_invitation_code():
    """Генерирует случайный код приглашения"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_pair_code(db: Session):
    """Генерирует новый код приглашения"""
    code = generate_invitation_code()
    
    while db.query(PartnerPair).filter(PartnerPair.invitation_code == code).first():
        code = generate_invitation_code()
    
    return code

def join_pair(db: Session, code: str, user_id: str):
    """Присоединиться к паре по коду приглашения"""
    pair = db.query(PartnerPair).filter(PartnerPair.invitation_code == code).first()
    
    if not pair:
        return None
    
    if pair.user2_id is not None:
        raise HTTPException(status_code=400, detail="Pair is already full")
    
    if pair.user1_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot join your own pair")
    
    pair.user2_id = user_id
    db.commit()
    db.refresh(pair)
    
    return pair

def get_all_pairs(db: Session):
    return db.query(PartnerPair).all()

def create_idea(db: Session, idea: IdeaCreate):
    db_idea = Idea(**idea.dict())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

def get_all_ideas(db: Session):
    return db.query(Idea).all()

def get_idea(db: Session, idea_id: str):
    return db.query(Idea).filter(Idea.idea_id == idea_id).first()

def delete_idea(db: Session, idea_id: str):
    db.query(Idea).filter(Idea.idea_id == idea_id).delete()
    db.commit()

def update_idea(db: Session, idea_id: str, updated_idea: dict):
    db.query(Idea).filter(Idea.idea_id == idea_id).update(updated_idea)
    db.commit()

def create_date_event(db: Session, event: DateEventCreate):
    db_event = DateEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def respond_to_proposal(db: Session, proposal_id: str, accepted: bool):
    event = db.query(DateEvent).filter(DateEvent.id == proposal_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    event.accepted = accepted
    if accepted:
        event.date_status = "accepted"
    else:
        event.date_status = "cancelled"
    
    db.commit()
    db.refresh(event)
    return event

def get_date_history(db: Session, pair_id: str):
    return db.query(DateEvent).filter(DateEvent.pair_id == pair_id).all()