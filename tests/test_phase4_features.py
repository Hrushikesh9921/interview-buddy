"""
Tests for Phase 4 features: Timer System & Resource Enforcement.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession

from models.models import Session, SessionStatus
from services.session_service import get_session_service, SessionConfig
from services.timer_service import get_timer_service
from services.token_service import get_token_service
from config.constants import TimerState


@pytest.fixture
def sample_session(test_db: DBSession):
    """Create a sample session for testing."""
    session_service = get_session_service()
    
    config = SessionConfig(
        candidate_name="Test Candidate",
        candidate_email="test@example.com",
        time_limit=3600,  # 1 hour
        token_budget=50000,
        model_name="gpt-4",
        challenge_text="Test challenge"
    )
    
    session = session_service.create_session(config, test_db)
    return session


class TestTimerExtension:
    """Test timer extension functionality."""
    
    def test_extend_time(self, test_db: DBSession, sample_session: Session):
        """Test extending session time limit."""
        session_service = get_session_service()
        
        # Get initial time limit
        initial_limit = sample_session.time_limit
        
        # Extend by 15 minutes
        updated = session_service.extend_time(sample_session.id, 15, test_db)
        
        assert updated is not None
        assert updated.time_limit == initial_limit + (15 * 60)
    
    def test_extend_time_completed_session(self, test_db: DBSession, sample_session: Session):
        """Test that completed sessions cannot be extended."""
        session_service = get_session_service()
        
        # Complete the session
        sample_session.status = SessionStatus.COMPLETED
        test_db.commit()
        
        initial_limit = sample_session.time_limit
        
        # Try to extend
        updated = session_service.extend_time(sample_session.id, 15, test_db)
        
        # Should return session but not extend
        assert updated.time_limit == initial_limit


class TestTokenExtension:
    """Test token budget extension functionality."""
    
    def test_extend_tokens(self, test_db: DBSession, sample_session: Session):
        """Test extending token budget."""
        session_service = get_session_service()
        
        # Get initial budget
        initial_budget = sample_session.token_budget
        
        # Extend by 10,000 tokens
        updated = session_service.extend_tokens(sample_session.id, 10000, test_db)
        
        assert updated is not None
        assert updated.token_budget == initial_budget + 10000
    
    def test_extend_tokens_completed_session(self, test_db: DBSession, sample_session: Session):
        """Test that completed sessions cannot have tokens extended."""
        session_service = get_session_service()
        
        # Complete the session
        sample_session.status = SessionStatus.COMPLETED
        test_db.commit()
        
        initial_budget = sample_session.token_budget
        
        # Try to extend
        updated = session_service.extend_tokens(sample_session.id, 10000, test_db)
        
        # Should return session but not extend
        assert updated.token_budget == initial_budget


class TestWarningThresholds:
    """Test warning threshold detection."""
    
    def test_timer_warning_levels(self, test_db: DBSession, sample_session: Session):
        """Test timer warning level detection."""
        timer_service = get_timer_service()
        
        # Start session
        sample_session.start_time = datetime.utcnow()
        sample_session.status = SessionStatus.ACTIVE
        sample_session.time_limit = 3600  # 1 hour
        test_db.commit()
        
        # Test normal level (> 25% remaining)
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=1800)  # 30 min elapsed
        test_db.commit()
        warning_level = timer_service.get_warning_level(sample_session)
        assert warning_level == "normal"
        
        # Test warning level (10-25% remaining)
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3000)  # 50 min elapsed
        test_db.commit()
        warning_level = timer_service.get_warning_level(sample_session)
        assert warning_level == "warning"
        
        # Test critical level (<= 10% remaining)
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3480)  # 58 min elapsed
        test_db.commit()
        warning_level = timer_service.get_warning_level(sample_session)
        assert warning_level == "critical"
        
        # Test expired
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3700)  # > 1 hour
        test_db.commit()
        warning_level = timer_service.get_warning_level(sample_session)
        assert warning_level == "expired"
    
    def test_timer_warning_messages(self, test_db: DBSession, sample_session: Session):
        """Test timer warning messages."""
        timer_service = get_timer_service()
        
        # Start session
        sample_session.start_time = datetime.utcnow()
        sample_session.status = SessionStatus.ACTIVE
        sample_session.time_limit = 3600  # 1 hour
        test_db.commit()
        
        # Normal - no warning
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=1800)
        test_db.commit()
        message = timer_service.get_warning_message(sample_session)
        assert message is None
        
        # Warning level
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3000)
        test_db.commit()
        message = timer_service.get_warning_message(sample_session)
        assert message is not None
        assert "Warning" in message or "⏳" in message
        
        # Critical level
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3480)
        test_db.commit()
        message = timer_service.get_warning_message(sample_session)
        assert message is not None
        assert "Critical" in message or "URGENT" in message
    
    def test_token_warning_levels(self, test_db: DBSession, sample_session: Session):
        """Test token warning level detection."""
        token_service = get_token_service()
        
        # Set up session with token budget
        sample_session.token_budget = 10000
        sample_session.tokens_used = 0
        test_db.commit()
        
        # Test normal level (< 75% used)
        sample_session.tokens_used = 5000
        test_db.commit()
        warning_level = token_service.get_warning_level(sample_session.id, test_db)
        assert warning_level == "normal"
        
        # Test warning level (75-90% used)
        sample_session.tokens_used = 8000
        test_db.commit()
        warning_level = token_service.get_warning_level(sample_session.id, test_db)
        assert warning_level == "warning"
        
        # Test critical level (> 90% used)
        sample_session.tokens_used = 9500
        test_db.commit()
        warning_level = token_service.get_warning_level(sample_session.id, test_db)
        assert warning_level == "critical"
        
        # Test exhausted
        sample_session.tokens_used = 10000
        test_db.commit()
        warning_level = token_service.get_warning_level(sample_session.id, test_db)
        assert warning_level == "exhausted"
    
    def test_token_warning_messages(self, test_db: DBSession, sample_session: Session):
        """Test token warning messages."""
        token_service = get_token_service()
        
        # Set up session
        sample_session.token_budget = 10000
        sample_session.tokens_used = 0
        test_db.commit()
        
        # Normal - no warning
        sample_session.tokens_used = 5000
        test_db.commit()
        message = token_service.get_warning_message(sample_session.id, test_db)
        assert message is None
        
        # Warning level
        sample_session.tokens_used = 8000
        test_db.commit()
        message = token_service.get_warning_message(sample_session.id, test_db)
        assert message is not None
        assert "Warning" in message or "⏳" in message
        
        # Critical level
        sample_session.tokens_used = 9500
        test_db.commit()
        message = token_service.get_warning_message(sample_session.id, test_db)
        assert message is not None
        assert "Critical" in message or "URGENT" in message


class TestEstimatedQueries:
    """Test estimated queries remaining calculation."""
    
    def test_estimate_queries_remaining(self, test_db: DBSession, sample_session: Session):
        """Test estimation of remaining queries."""
        token_service = get_token_service()
        
        # Set up session with usage
        sample_session.token_budget = 10000
        sample_session.tokens_used = 5000
        sample_session.message_count = 10
        test_db.commit()
        
        # Average = 500 tokens per message
        # Remaining = 5000 tokens
        # Estimated queries = 5000 / 500 = 10
        
        estimated = token_service.estimate_queries_remaining(sample_session.id, test_db)
        assert estimated == 10
    
    def test_estimate_queries_no_history(self, test_db: DBSession, sample_session: Session):
        """Test estimation with no message history."""
        token_service = get_token_service()
        
        # Set up session with no messages
        sample_session.token_budget = 10000
        sample_session.tokens_used = 0
        sample_session.message_count = 0
        test_db.commit()
        
        # Should return None (cannot estimate)
        estimated = token_service.estimate_queries_remaining(sample_session.id, test_db)
        assert estimated is None
    
    def test_estimate_queries_exhausted(self, test_db: DBSession, sample_session: Session):
        """Test estimation when budget is exhausted."""
        token_service = get_token_service()
        
        # Set up session with exhausted budget
        sample_session.token_budget = 10000
        sample_session.tokens_used = 10000
        sample_session.message_count = 20
        test_db.commit()
        
        # Should return 0
        estimated = token_service.estimate_queries_remaining(sample_session.id, test_db)
        assert estimated == 0


class TestThresholdCrossing:
    """Test threshold crossing detection."""
    
    def test_should_show_warning(self, test_db: DBSession, sample_session: Session):
        """Test warning display logic."""
        timer_service = get_timer_service()
        
        # Set up session
        sample_session.start_time = datetime.utcnow()
        sample_session.status = SessionStatus.ACTIVE
        sample_session.time_limit = 3600
        test_db.commit()
        
        # Cross 25% threshold
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=2800)  # ~22% remaining
        test_db.commit()
        should_warn = timer_service.should_show_warning(sample_session, last_warning_percentage=None)
        assert should_warn is True
        
        # Already warned at 25%, now at 22% - should not warn again
        should_warn = timer_service.should_show_warning(sample_session, last_warning_percentage=22)
        assert should_warn is False
        
        # Cross 10% threshold
        sample_session.start_time = datetime.utcnow() - timedelta(seconds=3300)  # ~8% remaining
        test_db.commit()
        should_warn = timer_service.should_show_warning(sample_session, last_warning_percentage=22)
        assert should_warn is True

