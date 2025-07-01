from sqlalchemy.orm import Session
from app.models import User, PartnerPair, Idea, DateEvent
from app.schemas import UserCreate, PartnerPairCreate, IdeaCreate, DateEventCreate
#* User 
def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

#* Pairs
def create_pair(db: Session, pair: PartnerPairCreate):
    db_pair = PartnerPair(**pair.dict())
    db.add(db_pair)
    db.commit()
    db.refresh(db_pair)
    return db_pair

def get_pair(db: Session, pair_id: str):
    return db.query(PartnerPair).filter(PartnerPair.id == pair_id).first()

def generate_pair_code(db: Session):
    pass

def join_pair(db: Session, code: str):
    pass

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

    pass

def get_date_history(db: Session):

    pass