from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from datetime import datetime

from . import models, schemas

# User CRUD
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    try:
        db_user = models.User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this telegram_id already exists")

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

# Pair CRUD
def create_pair(db: Session, pair: schemas.PartnerPairCreate) -> models.PartnerPair:
    try:
        db_pair = models.PartnerPair(**pair.dict())
        db.add(db_pair)
        db.commit()
        db.refresh(db_pair)
        return db_pair
    except IntegrityError:
        db.rollback()
        raise ValueError("Cannot create pair - users don't exist")

def get_pair(db: Session, pair_id: str) -> Optional[models.PartnerPair]:
    return db.query(models.PartnerPair).filter(models.PartnerPair.id == pair_id).first()

def get_all_pairs(db: Session, skip: int = 0, limit: int = 100) -> List[models.PartnerPair]:
    return db.query(models.PartnerPair).offset(skip).limit(limit).all()

def generate_pair_code(db: Session) -> str:
    """Генерирует уникальный код для присоединения к паре"""
    # Простая реализация - в реальности нужно сохранять коды в БД
    return str(uuid.uuid4())[:8].upper()

def join_pair(db: Session, code: str) -> Optional[models.PartnerPair]:
    """Присоединение к паре по коду - требует дополнительной логики"""
    # Заглушка - в реальности нужна таблица для хранения кодов
    return None

# Idea CRUD
def create_idea(db: Session, idea: schemas.IdeaCreate) -> models.Idea:
    try:
        db_idea = models.Idea(**idea.dict())
        db.add(db_idea)
        db.commit()
        db.refresh(db_idea)
        return db_idea
    except IntegrityError:
        db.rollback()
        raise ValueError("Idea with this ID already exists")

def get_idea(db: Session, idea_id: str) -> Optional[models.Idea]:
    return db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()

def get_all_ideas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Idea]:
    return db.query(models.Idea).offset(skip).limit(limit).all()

def update_idea(db: Session, idea_id: str, idea_update: schemas.IdeaUpdate) -> Optional[models.Idea]:
    db_idea = get_idea(db, idea_id)
    if not db_idea:
        return None
    
    update_data = idea_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_idea, field, value)
    
    db.commit()
    db.refresh(db_idea)
    return db_idea

def delete_idea(db: Session, idea_id: str) -> bool:
    db_idea = get_idea(db, idea_id)
    if not db_idea:
        return False
    
    db.delete(db_idea)
    db.commit()
    return True

# DateEvent CRUD
def create_date_event(db: Session, event: schemas.DateEventCreate) -> models.DateEvent:
    try:
        db_event = models.DateEvent(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError:
        db.rollback()
        raise ValueError("Cannot create event - referenced entities don't exist")

def respond_to_proposal(db: Session, proposal_id: str, accepted: bool) -> Optional[models.DateEvent]:
    db_event = db.query(models.DateEvent).filter(models.DateEvent.id == proposal_id).first()
    if not db_event:
        return None
    
    db_event.accepted = accepted
    db_event.date_status = "accepted" if accepted else "cancelled"
    
    db.commit()
    db.refresh(db_event)
    return db_event

def get_date_history(db: Session, skip: int = 0, limit: int = 100) -> List[models.DateEvent]:
    return db.query(models.DateEvent).offset(skip).limit(limit).all()

def get_date_event(db: Session, event_id: str) -> Optional[models.DateEvent]:
    return db.query(models.DateEvent).filter(models.DateEvent.id == event_id).first()