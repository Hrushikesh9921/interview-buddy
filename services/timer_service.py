"""
Timer service for tracking session time limits.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session as DBSession
import logging

from models.models import Session, SessionStatus
from config.constants import TimerState

logger = logging.getLogger(__name__)


class TimerInfo:
    """Represents timer information for a session."""
    
    def __init__(
        self,
        session_id: str,
        state: TimerState,
        elapsed_seconds: int,
        remaining_seconds: int,
        time_limit: int,
        is_expired: bool,
        start_time: Optional[datetime] = None,
        paused_at: Optional[datetime] = None
    ):
        self.session_id = session_id
        self.state = state
        self.elapsed_seconds = elapsed_seconds
        self.remaining_seconds = remaining_seconds
        self.time_limit = time_limit
        self.is_expired = is_expired
        self.start_time = start_time
        self.paused_at = paused_at
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "elapsed_seconds": self.elapsed_seconds,
            "remaining_seconds": self.remaining_seconds,
            "time_limit": self.time_limit,
            "is_expired": self.is_expired,
            "percentage_used": round((self.elapsed_seconds / self.time_limit * 100), 2) if self.time_limit > 0 else 0,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None
        }


class TimerService:
    """Service for managing session timers."""
    
    def __init__(self):
        pass
    
    def get_timer_state(self, session: Session) -> TimerState:
        """Determine the current timer state."""
        if not session.start_time:
            return TimerState.NOT_STARTED
        
        if session.status == SessionStatus.PAUSED:
            return TimerState.PAUSED
        
        if session.status == SessionStatus.COMPLETED:
            return TimerState.EXPIRED
        
        if session.status == SessionStatus.ACTIVE:
            if self.is_expired(session):
                return TimerState.EXPIRED
            return TimerState.RUNNING
        
        return TimerState.NOT_STARTED
    
    def get_elapsed_time(self, session: Session) -> int:
        """
        Get elapsed time in seconds.
        
        Calculates time from start_time to now (or end_time),
        excluding paused duration.
        
        Returns:
            Elapsed seconds
        """
        if not session.start_time:
            return 0
        
        # Determine end point
        if session.end_time:
            end_point = session.end_time
        elif session.paused_at:
            end_point = session.paused_at
        else:
            end_point = datetime.utcnow()
        
        # Calculate raw elapsed time
        total_elapsed = (end_point - session.start_time).total_seconds()
        
        # Subtract paused duration
        paused_duration = session.total_paused_duration or 0
        
        # Add current pause if session is paused
        if session.paused_at and not session.end_time:
            current_pause = (datetime.utcnow() - session.paused_at).total_seconds()
            paused_duration += current_pause
        
        active_elapsed = total_elapsed - paused_duration
        
        return max(0, int(active_elapsed))
    
    def get_remaining_time(self, session: Session) -> int:
        """
        Get remaining time in seconds.
        
        Returns:
            Remaining seconds (0 if expired)
        """
        elapsed = self.get_elapsed_time(session)
        remaining = session.time_limit - elapsed
        return max(0, remaining)
    
    def is_expired(self, session: Session) -> bool:
        """Check if session timer has expired."""
        if not session.start_time:
            return False
        
        if session.status == SessionStatus.COMPLETED:
            return True
        
        elapsed = self.get_elapsed_time(session)
        return elapsed >= session.time_limit
    
    def get_timer_info(self, session: Session) -> TimerInfo:
        """
        Get comprehensive timer information.
        
        Args:
            session: Session object
        
        Returns:
            TimerInfo object
        """
        state = self.get_timer_state(session)
        elapsed = self.get_elapsed_time(session)
        remaining = self.get_remaining_time(session)
        is_expired = self.is_expired(session)
        
        return TimerInfo(
            session_id=session.id,
            state=state,
            elapsed_seconds=elapsed,
            remaining_seconds=remaining,
            time_limit=session.time_limit,
            is_expired=is_expired,
            start_time=session.start_time,
            paused_at=session.paused_at
        )
    
    def format_time(self, seconds: int) -> str:
        """
        Format seconds as HH:MM:SS.
        
        Args:
            seconds: Time in seconds
        
        Returns:
            Formatted time string
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_warning_level(self, session: Session) -> str:
        """
        Get warning level based on remaining time percentage.
        
        Returns:
            "normal", "warning", "critical", or "expired"
        """
        if self.is_expired(session):
            return "expired"
        
        remaining = self.get_remaining_time(session)
        percentage_remaining = (remaining / session.time_limit) * 100 if session.time_limit > 0 else 100
        
        if percentage_remaining <= 10:
            return "critical"
        elif percentage_remaining <= 25:
            return "warning"
        else:
            return "normal"


# Global service instance
_timer_service: Optional[TimerService] = None


def get_timer_service() -> TimerService:
    """Get or create the global timer service instance."""
    global _timer_service
    if _timer_service is None:
        _timer_service = TimerService()
    return _timer_service

