"""
Tests for configuration and settings.
"""
import pytest
from config.settings import Settings
from config.constants import (
    SessionStatus, MessageRole, UserType, 
    ChallengeCategory, ChallengeDifficulty,
    TimerState, EventType
)


class TestSettings:
    """Test Settings class."""
    
    def test_settings_initialization(self, test_settings):
        """Test settings initialization."""
        assert test_settings.openai_api_key == "sk-test-key"
        assert test_settings.openai_model == "gpt-4"
        assert test_settings.database_url == "sqlite:///:memory:"
        assert test_settings.debug is True
    
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings(openai_api_key="test")
        assert settings.default_session_duration == 3600
        assert settings.default_token_budget == 50000
        assert settings.max_message_length == 5000
        assert settings.openai_model == "gpt-4"
    
    def test_validate_openai_key(self, test_settings):
        """Test OpenAI key validation."""
        assert test_settings.validate_openai_key() is True
        
        settings_no_key = Settings(openai_api_key="")
        assert settings_no_key.validate_openai_key() is False
    
    def test_warning_thresholds_parsing(self, test_settings):
        """Test warning thresholds parsing."""
        thresholds = test_settings.warning_thresholds
        assert isinstance(thresholds, list)
        assert len(thresholds) == 3
        assert all(isinstance(t, int) for t in thresholds)


class TestConstants:
    """Test application constants."""
    
    def test_session_status_enum(self):
        """Test SessionStatus enumeration."""
        assert SessionStatus.CREATED == "created"
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.PAUSED == "paused"
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.EXPIRED == "expired"
    
    def test_message_role_enum(self):
        """Test MessageRole enumeration."""
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
    
    def test_user_type_enum(self):
        """Test UserType enumeration."""
        assert UserType.CANDIDATE == "candidate"
        assert UserType.INTERVIEWER == "interviewer"
    
    def test_challenge_category_enum(self):
        """Test ChallengeCategory enumeration."""
        assert ChallengeCategory.ALGORITHMS == "algorithms"
        assert ChallengeCategory.DATA_STRUCTURES == "data_structures"
        assert ChallengeCategory.SYSTEM_DESIGN == "system_design"
    
    def test_challenge_difficulty_enum(self):
        """Test ChallengeDifficulty enumeration."""
        assert ChallengeDifficulty.EASY == "easy"
        assert ChallengeDifficulty.MEDIUM == "medium"
        assert ChallengeDifficulty.HARD == "hard"
    
    def test_timer_state_enum(self):
        """Test TimerState enumeration."""
        assert TimerState.NOT_STARTED == "not_started"
        assert TimerState.RUNNING == "running"
        assert TimerState.PAUSED == "paused"
        assert TimerState.EXPIRED == "expired"
    
    def test_event_type_enum(self):
        """Test EventType enumeration."""
        assert EventType.SESSION_CREATED == "session_created"
        assert EventType.SESSION_STARTED == "session_started"
        assert EventType.MESSAGE_SENT == "message_sent"

