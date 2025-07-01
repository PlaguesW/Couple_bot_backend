from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PartnerPair(Base):
    __tablename__ = "pairs"
    id = Column(String, primary_key=True, index=True)
    user1_id = Column(String, ForeignKey("users.user_id"))
    user2_id = Column(String, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Idea(Base):
    __tablename__ = "ideas"
    idea_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DateEvent(Base):
    __tablename__ = "date_events"
    id = Column(String, primary_key=True, index=True)
    pair_id = Column(String, ForeignKey("pairs.id"))
    idea_id = Column(String, ForeignKey("ideas.idea_id"))
    proposer_id = Column(String, ForeignKey("users.user_id"))
    accepted = Column(Boolean, default=False)
    date_status = Column(Enum("pending", "accepted", "completed", "cancelled", name="date_status_enum"))
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)