"""
Tests for token service.
"""
import pytest
from services.token_service import TokenService, TokenUsage, get_token_service
from models import Session
from config.constants import SessionStatus


class TestTokenUsage:
    """Test TokenUsage class."""
    
    def test_token_usage_initialization(self):
        """Test TokenUsage initialization."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            remaining_budget=850,
            budget_percentage_used=15.0
        )
        
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.remaining_budget == 850
        assert usage.budget_percentage_used == 15.0
    
    def test_token_usage_to_dict(self):
        """Test TokenUsage to_dict method."""
        usage = TokenUsage(100, 50, 150, 850, 15.0)
        usage_dict = usage.to_dict()
        
        assert usage_dict["input_tokens"] == 100
        assert usage_dict["output_tokens"] == 50
        assert usage_dict["total_tokens"] == 150
        assert usage_dict["remaining_budget"] == 850
        assert usage_dict["budget_percentage_used"] == 15.0


class TestTokenService:
    """Test TokenService class."""
    
    def test_service_initialization(self):
        """Test service initialization."""
        service = TokenService()
        assert service is not None
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        service = TokenService()
        
        text = "Hello, world!"
        estimated = service.estimate_tokens(text)
        
        assert estimated > 0
        assert estimated < 10
    
    def test_reserve_tokens_success(self, test_db):
        """Test successful token reservation."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=100,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        # Reserve tokens
        result = service.reserve_tokens(session.id, 200, test_db)
        assert result is True
    
    def test_reserve_tokens_insufficient_budget(self, test_db):
        """Test token reservation with insufficient budget."""
        service = TokenService()
        
        # Create a test session with limited budget
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=950,  # Only 50 remaining
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        # Try to reserve more than available
        result = service.reserve_tokens(session.id, 100, test_db)
        assert result is False
    
    def test_reserve_tokens_inactive_session(self, test_db):
        """Test token reservation for inactive session."""
        service = TokenService()
        
        # Create a completed session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=100,
            status=SessionStatus.COMPLETED
        )
        test_db.add(session)
        test_db.commit()
        
        # Try to reserve tokens
        result = service.reserve_tokens(session.id, 100, test_db)
        assert result is False
    
    def test_reserve_tokens_nonexistent_session(self, test_db):
        """Test token reservation for nonexistent session."""
        service = TokenService()
        
        result = service.reserve_tokens("nonexistent-id", 100, test_db)
        assert result is False
    
    def test_update_consumption(self, test_db):
        """Test updating token consumption."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        # Update consumption
        usage = service.update_consumption(session.id, 100, 50, test_db)
        
        assert usage is not None
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.remaining_budget == 850
        assert usage.budget_percentage_used == 15.0
        
        # Verify database was updated
        test_db.refresh(session)
        assert session.tokens_used == 150
        assert session.input_tokens == 100
        assert session.output_tokens == 50
    
    def test_update_consumption_multiple_times(self, test_db):
        """Test updating consumption multiple times."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        # First update
        usage1 = service.update_consumption(session.id, 100, 50, test_db)
        assert usage1.total_tokens == 150
        
        # Second update
        usage2 = service.update_consumption(session.id, 80, 40, test_db)
        assert usage2.total_tokens == 270  # 150 + 120
        assert usage2.input_tokens == 180  # 100 + 80
        assert usage2.output_tokens == 90  # 50 + 40
    
    def test_get_remaining_budget(self, test_db):
        """Test getting remaining budget."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=300,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        remaining = service.get_remaining_budget(session.id, test_db)
        assert remaining == 700
    
    def test_get_remaining_budget_exhausted(self, test_db):
        """Test getting remaining budget when exhausted."""
        service = TokenService()
        
        # Create a test session with budget exhausted
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=1200,  # Over budget
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        remaining = service.get_remaining_budget(session.id, test_db)
        assert remaining == 0  # Should return 0, not negative
    
    def test_check_budget_sufficient(self, test_db):
        """Test checking budget when sufficient."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=300,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        result = service.check_budget(session.id, 500, test_db)
        assert result is True
    
    def test_check_budget_insufficient(self, test_db):
        """Test checking budget when insufficient."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=900,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        result = service.check_budget(session.id, 200, test_db)
        assert result is False
    
    def test_get_usage_stats(self, test_db):
        """Test getting usage statistics."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=300,
            input_tokens=200,
            output_tokens=100,
            message_count=5,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        stats = service.get_usage_stats(session.id, test_db)
        
        assert stats is not None
        assert stats["token_budget"] == 1000
        assert stats["tokens_used"] == 300
        assert stats["input_tokens"] == 200
        assert stats["output_tokens"] == 100
        assert stats["remaining_budget"] == 700
        assert stats["percentage_used"] == 30.0
        assert stats["message_count"] == 5
        assert stats["avg_tokens_per_message"] == 60.0
    
    def test_is_budget_exhausted_false(self, test_db):
        """Test checking if budget is exhausted when it's not."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=500,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        result = service.is_budget_exhausted(session.id, test_db)
        assert result is False
    
    def test_is_budget_exhausted_true(self, test_db):
        """Test checking if budget is exhausted when it is."""
        service = TokenService()
        
        # Create a test session
        session = Session(
            candidate_name="Test User",
            time_limit=3600,
            token_budget=1000,
            tokens_used=1000,
            status=SessionStatus.ACTIVE
        )
        test_db.add(session)
        test_db.commit()
        
        result = service.is_budget_exhausted(session.id, test_db)
        assert result is True


class TestTokenServiceGlobal:
    """Test global token service functions."""
    
    def test_get_token_service(self):
        """Test getting global service instance."""
        service1 = get_token_service()
        service2 = get_token_service()
        
        # Should return same instance
        assert service1 is service2

