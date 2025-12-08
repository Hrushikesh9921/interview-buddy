"""
Database models for Interview Buddy application.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
import uuid

from models.database import Base
from config.constants import (
    SessionStatus, MessageRole, ChallengeCategory,
    ChallengeDifficulty, TimerState, EventType
)


def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


class Session(Base):
    """Session model representing an interview session."""
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Candidate information
    candidate_name = Column(String(255), nullable=False)
    candidate_email = Column(String(255), nullable=True)
    
    # Session configuration
    time_limit = Column(Integer, nullable=False)  # seconds
    token_budget = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False, default="gpt-4")
    
    # Session state
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.CREATED, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    total_paused_duration = Column(Integer, default=0)  # seconds
    
    # Resource tracking
    tokens_used = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    
    # Challenge
    challenge_id = Column(String(36), ForeignKey("challenges.id"), nullable=True)
    challenge_text = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Additional configuration (JSON)
    config = Column(JSON, nullable=True)
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    events = relationship("SessionEvent", back_populates="session", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="session", uselist=False, cascade="all, delete-orphan")
    challenge = relationship("Challenge", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_status", "status"),
        Index("idx_session_created_at", "created_at"),
        Index("idx_session_candidate_email", "candidate_email"),
    )
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, candidate={self.candidate_name}, status={self.status})>"


class Message(Base):
    """Message model representing chat messages in a session."""
    
    __tablename__ = "messages"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    
    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Token tracking
    tokens = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_message_session_id", "session_id"),
        Index("idx_message_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


class Challenge(Base):
    """Challenge model representing interview challenges."""
    
    __tablename__ = "challenges"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Challenge details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ChallengeCategory), nullable=False)
    difficulty = Column(SQLEnum(ChallengeDifficulty), nullable=False)
    
    # Challenge content
    instructions = Column(Text, nullable=True)
    starter_code = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=True)
    hints = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Additional metadata
    tags = Column(JSON, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds
    
    # Relationships
    sessions = relationship("Session", back_populates="challenge")
    
    # Indexes
    __table_args__ = (
        Index("idx_challenge_category", "category"),
        Index("idx_challenge_difficulty", "difficulty"),
        Index("idx_challenge_is_template", "is_template"),
    )
    
    def __repr__(self) -> str:
        return f"<Challenge(id={self.id}, title={self.title}, difficulty={self.difficulty})>"


class SessionEvent(Base):
    """Session event model for tracking session activities."""
    
    __tablename__ = "session_events"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    
    # Event details
    event_type = Column(SQLEnum(EventType), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index("idx_event_session_id", "session_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<SessionEvent(id={self.id}, type={self.event_type}, session_id={self.session_id})>"


class Analytics(Base):
    """Analytics model for storing session analytics."""
    
    __tablename__ = "analytics"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Foreign key (one-to-one with Session)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, unique=True)
    
    # Efficiency metrics
    token_efficiency_score = Column(Float, nullable=True)
    time_utilization = Column(Float, nullable=True)
    messages_per_minute = Column(Float, nullable=True)
    avg_tokens_per_message = Column(Float, nullable=True)
    
    # Performance metrics
    total_duration = Column(Integer, nullable=True)  # seconds
    active_duration = Column(Integer, nullable=True)  # seconds (excluding pauses)
    completion_percentage = Column(Float, nullable=True)
    
    # Token usage breakdown
    token_usage_timeline = Column(JSON, nullable=True)
    
    # Additional analytics
    analytics_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="analytics")
    
    # Indexes
    __table_args__ = (
        Index("idx_analytics_session_id", "session_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Analytics(id={self.id}, session_id={self.session_id})>"

