"""
Tests for Timer Service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from services.timer_service import TimerService, TimerInfo, get_timer_service
from models.models import Session
from config.constants import SessionStatus, TimerState


@pytest.fixture
def timer_service():
    """Create a timer service instance."""
    return TimerService()


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = Mock(spec=Session)
    session.id = "test-session-id"
    session.time_limit = 3600  # 1 hour
    session.start_time = None
    session.end_time = None
    session.paused_at = None
    session.total_paused_duration = 0
    session.status = SessionStatus.CREATED
    return session


class TestTimerService:
    """Test timer service functionality."""
    
    def test_get_timer_service(self):
        """Test getting global timer service instance."""
        service1 = get_timer_service()
        service2 = get_timer_service()
        assert service1 is service2  # Should be singleton
    
    def test_timer_state_not_started(self, timer_service, mock_session):
        """Test timer state for not started session."""
        state = timer_service.get_timer_state(mock_session)
        assert state == TimerState.NOT_STARTED
    
    def test_timer_state_running(self, timer_service, mock_session):
        """Test timer state for running session."""
        mock_session.start_time = datetime.utcnow()
        mock_session.status = SessionStatus.ACTIVE
        
        state = timer_service.get_timer_state(mock_session)
        assert state == TimerState.RUNNING
    
    def test_timer_state_paused(self, timer_service, mock_session):
        """Test timer state for paused session."""
        mock_session.start_time = datetime.utcnow()
        mock_session.status = SessionStatus.PAUSED
        mock_session.paused_at = datetime.utcnow()
        
        state = timer_service.get_timer_state(mock_session)
        assert state == TimerState.PAUSED
    
    def test_timer_state_expired(self, timer_service, mock_session):
        """Test timer state for expired session."""
        mock_session.start_time = datetime.utcnow() - timedelta(hours=2)
        mock_session.status = SessionStatus.COMPLETED
        
        state = timer_service.get_timer_state(mock_session)
        assert state == TimerState.EXPIRED
    
    def test_get_elapsed_time_not_started(self, timer_service, mock_session):
        """Test elapsed time for not started session."""
        elapsed = timer_service.get_elapsed_time(mock_session)
        assert elapsed == 0
    
    def test_get_elapsed_time_active(self, timer_service, mock_session):
        """Test elapsed time for active session."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=10)
        mock_session.status = SessionStatus.ACTIVE
        
        elapsed = timer_service.get_elapsed_time(mock_session)
        assert 590 <= elapsed <= 610  # ~10 minutes (allow some tolerance)
    
    def test_get_elapsed_time_with_pause(self, timer_service, mock_session):
        """Test elapsed time excludes paused duration."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=20)
        mock_session.total_paused_duration = 300  # 5 minutes paused
        mock_session.status = SessionStatus.ACTIVE
        
        elapsed = timer_service.get_elapsed_time(mock_session)
        # Should be ~15 minutes (20 - 5)
        assert 890 <= elapsed <= 910
    
    def test_get_remaining_time(self, timer_service, mock_session):
        """Test remaining time calculation."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=10)
        mock_session.time_limit = 1800  # 30 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        remaining = timer_service.get_remaining_time(mock_session)
        # Should be ~20 minutes (30 - 10)
        assert 1190 <= remaining <= 1210
    
    def test_get_remaining_time_expired(self, timer_service, mock_session):
        """Test remaining time returns 0 when expired."""
        mock_session.start_time = datetime.utcnow() - timedelta(hours=2)
        mock_session.time_limit = 3600  # 1 hour
        mock_session.status = SessionStatus.ACTIVE
        
        remaining = timer_service.get_remaining_time(mock_session)
        assert remaining == 0
    
    def test_is_expired_not_started(self, timer_service, mock_session):
        """Test is_expired for not started session."""
        assert not timer_service.is_expired(mock_session)
    
    def test_is_expired_active_not_expired(self, timer_service, mock_session):
        """Test is_expired for active session within time limit."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=10)
        mock_session.time_limit = 1800  # 30 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        assert not timer_service.is_expired(mock_session)
    
    def test_is_expired_active_expired(self, timer_service, mock_session):
        """Test is_expired for active session past time limit."""
        mock_session.start_time = datetime.utcnow() - timedelta(hours=2)
        mock_session.time_limit = 3600  # 1 hour
        mock_session.status = SessionStatus.ACTIVE
        
        assert timer_service.is_expired(mock_session)
    
    def test_is_expired_completed(self, timer_service, mock_session):
        """Test is_expired for completed session."""
        mock_session.start_time = datetime.utcnow()
        mock_session.status = SessionStatus.COMPLETED
        
        assert timer_service.is_expired(mock_session)
    
    def test_get_timer_info(self, timer_service, mock_session):
        """Test getting comprehensive timer info."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=15)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        info = timer_service.get_timer_info(mock_session)
        
        assert isinstance(info, TimerInfo)
        assert info.session_id == "test-session-id"
        assert info.state == TimerState.RUNNING
        assert 890 <= info.elapsed_seconds <= 910  # ~15 minutes
        assert 2690 <= info.remaining_seconds <= 2710  # ~45 minutes
        assert info.time_limit == 3600
        assert not info.is_expired
    
    def test_format_time_hours(self, timer_service):
        """Test time formatting with hours."""
        formatted = timer_service.format_time(3665)
        assert formatted == "01:01:05"
    
    def test_format_time_minutes(self, timer_service):
        """Test time formatting without hours."""
        formatted = timer_service.format_time(125)
        assert formatted == "02:05"
    
    def test_format_time_zero(self, timer_service):
        """Test time formatting for zero."""
        formatted = timer_service.format_time(0)
        assert formatted == "00:00"
    
    def test_get_warning_level_normal(self, timer_service, mock_session):
        """Test warning level for normal time remaining."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=15)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        level = timer_service.get_warning_level(mock_session)
        assert level == "normal"
    
    def test_get_warning_level_warning(self, timer_service, mock_session):
        """Test warning level for warning threshold."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=50)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        level = timer_service.get_warning_level(mock_session)
        assert level == "warning"
    
    def test_get_warning_level_critical(self, timer_service, mock_session):
        """Test warning level for critical threshold."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=58)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        level = timer_service.get_warning_level(mock_session)
        assert level == "critical"
    
    def test_get_warning_level_expired(self, timer_service, mock_session):
        """Test warning level for expired session."""
        mock_session.start_time = datetime.utcnow() - timedelta(hours=2)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        level = timer_service.get_warning_level(mock_session)
        assert level == "expired"
    
    def test_timer_info_to_dict(self, timer_service, mock_session):
        """Test converting TimerInfo to dictionary."""
        mock_session.start_time = datetime.utcnow() - timedelta(minutes=30)
        mock_session.time_limit = 3600  # 60 minutes
        mock_session.status = SessionStatus.ACTIVE
        
        info = timer_service.get_timer_info(mock_session)
        info_dict = info.to_dict()
        
        assert isinstance(info_dict, dict)
        assert "session_id" in info_dict
        assert "state" in info_dict
        assert "elapsed_seconds" in info_dict
        assert "remaining_seconds" in info_dict
        assert "percentage_used" in info_dict
        assert 48 <= info_dict["percentage_used"] <= 52  # ~50%

