"""
Tests for database models and operations.
"""
import pytest
from datetime import datetime
from models.models import Session, Message, Challenge, SessionEvent, Analytics
from config.constants import (
    SessionStatus, MessageRole, ChallengeCategory,
    ChallengeDifficulty, EventType
)


class TestSessionModel:
    """Test Session model."""
    
    def test_create_session(self, test_db):
        """Test creating a session."""
        session = Session(
            candidate_name="John Doe",
            candidate_email="john@example.com",
            time_limit=3600,
            token_budget=50000,
            model_name="gpt-4",
            status=SessionStatus.CREATED
        )
        
        test_db.add(session)
        test_db.commit()
        
        assert session.id is not None
        assert session.candidate_name == "John Doe"
        assert session.status == SessionStatus.CREATED
        assert session.tokens_used == 0
        assert session.message_count == 0
    
    def test_session_defaults(self, test_db):
        """Test session default values."""
        session = Session(
            candidate_name="Jane Doe",
            time_limit=3600,
            token_budget=50000
        )
        
        test_db.add(session)
        test_db.commit()
        
        assert session.status == SessionStatus.CREATED
        assert session.tokens_used == 0
        assert session.input_tokens == 0
        assert session.output_tokens == 0
        assert session.message_count == 0
        assert session.total_paused_duration == 0
    
    def test_session_relationships(self, test_db):
        """Test session relationships."""
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=50000
        )
        
        test_db.add(session)
        test_db.commit()
        
        # Add message
        message = Message(
            session_id=session.id,
            role=MessageRole.USER,
            content="Hello",
            tokens=10
        )
        test_db.add(message)
        test_db.commit()
        
        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"


class TestMessageModel:
    """Test Message model."""
    
    def test_create_message(self, test_db):
        """Test creating a message."""
        session = Session(
            candidate_name="Test",
            time_limit=3600,
            token_budget=50000
        )
        test_db.add(session)
        test_db.commit()
        
        message = Message(
            session_id=session.id,
            role=MessageRole.USER,
            content="Test message",
            tokens=5
        )
        
        test_db.add(message)
        test_db.commit()
        
        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == "Test message"
        assert message.tokens == 5
        assert message.session_id == session.id


class TestChallengeModel:
    """Test Challenge model."""
    
    def test_create_challenge(self, test_db):
        """Test creating a challenge."""
        challenge = Challenge(
            title="Two Sum",
            description="Find two numbers that add up to target",
            category=ChallengeCategory.ALGORITHMS,
            difficulty=ChallengeDifficulty.EASY,
            instructions="Given an array...",
            is_template=True
        )
        
        test_db.add(challenge)
        test_db.commit()
        
        assert challenge.id is not None
        assert challenge.title == "Two Sum"
        assert challenge.difficulty == ChallengeDifficulty.EASY
        assert challenge.is_template is True
        assert challenge.is_active is True


class TestSessionEventModel:
    """Test SessionEvent model."""
    
    def test_create_event(self, test_db):
        """Test creating a session event."""
        session = Session(
            candidate_name="Test",
            time_limit=3600,
            token_budget=50000
        )
        test_db.add(session)
        test_db.commit()
        
        event = SessionEvent(
            session_id=session.id,
            event_type=EventType.SESSION_CREATED,
            description="Session created",
            data={"info": "test"}
        )
        
        test_db.add(event)
        test_db.commit()
        
        assert event.id is not None
        assert event.event_type == EventType.SESSION_CREATED
        assert event.data["info"] == "test"


class TestAnalyticsModel:
    """Test Analytics model."""
    
    def test_create_analytics(self, test_db):
        """Test creating analytics."""
        session = Session(
            candidate_name="Test",
            time_limit=3600,
            token_budget=50000
        )
        test_db.add(session)
        test_db.commit()
        
        analytics = Analytics(
            session_id=session.id,
            token_efficiency_score=0.85,
            time_utilization=0.90,
            messages_per_minute=2.5,
            avg_tokens_per_message=150.0
        )
        
        test_db.add(analytics)
        test_db.commit()
        
        assert analytics.id is not None
        assert analytics.session_id == session.id
        assert analytics.token_efficiency_score == 0.85
        assert analytics.time_utilization == 0.90

