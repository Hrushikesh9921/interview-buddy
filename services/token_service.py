"""
Token service for managing token budgets and tracking usage.
"""
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from models import Session, get_db_context
from utils.token_counter import count_tokens, count_message_tokens
from utils.logger import logger
from config.constants import SessionStatus


class TokenUsage:
    """Token usage information."""
    
    def __init__(
        self,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        remaining_budget: int,
        budget_percentage_used: float
    ):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.remaining_budget = remaining_budget
        self.budget_percentage_used = budget_percentage_used
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "remaining_budget": self.remaining_budget,
            "budget_percentage_used": self.budget_percentage_used
        }


class TokenService:
    """Service for managing token budgets and tracking usage."""
    
    def __init__(self):
        """Initialize token service."""
        pass
    
    def estimate_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        Estimate tokens for a text string.
        
        Args:
            text: Text to estimate tokens for
            model: Model to use for estimation
            
        Returns:
            Estimated number of tokens
        """
        return count_tokens(text, model)
    
    def reserve_tokens(
        self, 
        session_id: str, 
        estimated: int,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Reserve tokens for a message (pre-flight check).
        
        Args:
            session_id: Session ID
            estimated: Estimated tokens to reserve
            db: Database session (optional)
            
        Returns:
            True if tokens can be reserved, False otherwise
        """
        if db:
            return self._reserve_tokens_with_db(session_id, estimated, db)
        
        with get_db_context() as db:
            return self._reserve_tokens_with_db(session_id, estimated, db)
    
    def _reserve_tokens_with_db(
        self,
        session_id: str,
        estimated: int,
        db: DBSession
    ) -> bool:
        """Internal method to reserve tokens with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return False
        
        # Check if session is active
        if session.status not in [SessionStatus.CREATED, SessionStatus.ACTIVE]:
            logger.warning(f"Session {session_id} is not active (status: {session.status})")
            return False
        
        # Check budget
        remaining = session.token_budget - session.tokens_used
        
        if estimated > remaining:
            logger.warning(
                f"Insufficient tokens for session {session_id}: "
                f"need {estimated}, have {remaining}"
            )
            return False
        
        logger.info(f"Reserved {estimated} tokens for session {session_id}")
        return True
    
    def update_consumption(
        self,
        session_id: str,
        input_tokens: int,
        output_tokens: int,
        db: Optional[DBSession] = None
    ) -> Optional[TokenUsage]:
        """
        Update token consumption for a session.
        
        Args:
            session_id: Session ID
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            db: Database session (optional)
            
        Returns:
            TokenUsage object with updated information
        """
        if db:
            return self._update_consumption_with_db(
                session_id, input_tokens, output_tokens, db
            )
        
        with get_db_context() as db:
            return self._update_consumption_with_db(
                session_id, input_tokens, output_tokens, db
            )
    
    def _update_consumption_with_db(
        self,
        session_id: str,
        input_tokens: int,
        output_tokens: int,
        db: DBSession
    ) -> Optional[TokenUsage]:
        """Internal method to update consumption with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        # Update token counts
        total_tokens = input_tokens + output_tokens
        session.input_tokens += input_tokens
        session.output_tokens += output_tokens
        session.tokens_used += total_tokens
        session.updated_at = datetime.utcnow()
        
        # Calculate remaining budget
        remaining = session.token_budget - session.tokens_used
        percentage_used = (session.tokens_used / session.token_budget) * 100
        
        db.commit()
        
        logger.info(
            f"Updated token consumption for session {session_id}: "
            f"+{total_tokens} tokens (input: {input_tokens}, output: {output_tokens}), "
            f"total: {session.tokens_used}/{session.token_budget} ({percentage_used:.1f}%)"
        )
        
        return TokenUsage(
            input_tokens=session.input_tokens,
            output_tokens=session.output_tokens,
            total_tokens=session.tokens_used,
            remaining_budget=remaining,
            budget_percentage_used=percentage_used
        )
    
    def get_remaining_budget(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[int]:
        """
        Get remaining token budget for a session.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Remaining tokens, or None if session not found
        """
        if db:
            return self._get_remaining_budget_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._get_remaining_budget_with_db(session_id, db)
    
    def _get_remaining_budget_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[int]:
        """Internal method to get remaining budget with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        remaining = session.token_budget - session.tokens_used
        return max(0, remaining)
    
    def check_budget(
        self,
        session_id: str,
        estimated: int,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Check if session has enough budget for estimated tokens.
        
        Args:
            session_id: Session ID
            estimated: Estimated tokens needed
            db: Database session (optional)
            
        Returns:
            True if budget is sufficient, False otherwise
        """
        remaining = self.get_remaining_budget(session_id, db)
        
        if remaining is None:
            return False
        
        has_budget = estimated <= remaining
        
        if not has_budget:
            logger.warning(
                f"Insufficient budget for session {session_id}: "
                f"need {estimated}, have {remaining}"
            )
        
        return has_budget
    
    def get_usage_stats(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Dict]:
        """
        Get detailed usage statistics for a session.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Dictionary with usage statistics
        """
        if db:
            return self._get_usage_stats_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._get_usage_stats_with_db(session_id, db)
    
    def _get_usage_stats_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Dict]:
        """Internal method to get usage stats with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        remaining = session.token_budget - session.tokens_used
        percentage_used = (session.tokens_used / session.token_budget) * 100 if session.token_budget > 0 else 0
        
        avg_tokens_per_message = (
            session.tokens_used / session.message_count 
            if session.message_count > 0 
            else 0
        )
        
        return {
            "session_id": session_id,
            "token_budget": session.token_budget,
            "tokens_used": session.tokens_used,
            "input_tokens": session.input_tokens,
            "output_tokens": session.output_tokens,
            "remaining_budget": remaining,
            "percentage_used": percentage_used,
            "message_count": session.message_count,
            "avg_tokens_per_message": avg_tokens_per_message,
            "status": session.status.value
        }
    
    def is_budget_exhausted(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Check if session budget is exhausted.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            True if budget is exhausted, False otherwise
        """
        remaining = self.get_remaining_budget(session_id, db)
        
        if remaining is None:
            return True
        
        return remaining <= 0

    def get_warning_level(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> str:
        """
        Get warning level based on remaining token percentage.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            "normal", "warning", "critical", or "exhausted"
        """
        stats = self.get_usage_stats(session_id, db)
        
        if not stats:
            return "normal"
        
        percentage_remaining = 100 - stats["percentage_used"]
        
        if percentage_remaining <= 0:
            return "exhausted"
        elif percentage_remaining <= 5:
            return "critical"  # 5% or less - urgent
        elif percentage_remaining <= 10:
            return "critical"  # 10% or less - critical
        elif percentage_remaining <= 25:
            return "warning"   # 25% or less - warning
        else:
            return "normal"    # Above 25% - normal
    
    def get_warning_message(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[str]:
        """
        Get warning message based on remaining tokens.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Warning message string or None if no warning needed
        """
        stats = self.get_usage_stats(session_id, db)
        
        if not stats:
            return None
        
        remaining = stats["remaining_budget"]
        percentage_remaining = 100 - stats["percentage_used"]
        
        if remaining <= 0:
            return "🎫 Token budget exhausted! No more queries available."
        elif percentage_remaining <= 5:
            return f"🚨 URGENT: Only {remaining:,} tokens remaining!"
        elif percentage_remaining <= 10:
            return f"⚠️ Critical: {remaining:,} tokens left. Use wisely!"
        elif percentage_remaining <= 25:
            return f"⏳ Warning: {remaining:,} tokens remaining."
        
        return None
    
    def estimate_queries_remaining(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[int]:
        """
        Estimate how many more queries can be made based on average usage.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Estimated number of queries remaining, or None if cannot estimate
        """
        stats = self.get_usage_stats(session_id, db)
        
        if not stats or stats["message_count"] == 0:
            return None
        
        avg_tokens = stats["avg_tokens_per_message"]
        remaining = stats["remaining_budget"]
        
        if avg_tokens <= 0:
            return None
        
        estimated_queries = int(remaining / avg_tokens)
        return max(0, estimated_queries)


# Global token service instance
_token_service = None


def get_token_service() -> TokenService:
    """Get global token service instance."""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service

