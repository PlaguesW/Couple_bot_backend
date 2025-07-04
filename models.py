from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ProposalStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_pairs = relationship("Pair", foreign_keys="[Pair.user1_telegram_id]", back_populates="user1")
    joined_pairs = relationship("Pair", foreign_keys="[Pair.user2_telegram_id]", back_populates="user2")
    proposals = relationship("DateProposal", foreign_keys="[DateProposal.proposer_telegram_id]", back_populates="proposer")
    responses = relationship("DateProposal", foreign_keys="[DateProposal.responder_telegram_id]", back_populates="responder")

class Pair(Base):
    __tablename__ = "pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    user1_telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    user2_telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    is_complete = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_telegram_id], back_populates="created_pairs")
    user2 = relationship("User", foreign_keys=[user2_telegram_id], back_populates="joined_pairs")
    proposals = relationship("DateProposal", back_populates="pair")

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # romantic, home, cultural, active, budget
    duration = Column(String(50), nullable=True)  # 1-2 hours, 2-4 hours, full day, etc.
    cost_level = Column(String(20), nullable=False)  # free, low, medium, high
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proposals = relationship("DateProposal", back_populates="idea")

class DateProposal(Base):
    __tablename__ = "date_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    proposer_telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)
    responder_telegram_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=True)
    custom_description = Column(Text, nullable=True)
    proposed_date = Column(Date, nullable=True)
    proposed_time = Column(Time, nullable=True)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    response_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    pair = relationship("Pair", back_populates="proposals")
    proposer = relationship("User", foreign_keys=[proposer_telegram_id], back_populates="proposals")
    responder = relationship("User", foreign_keys=[responder_telegram_id], back_populates="responses")
    idea = relationship("Idea", back_populates="proposals")