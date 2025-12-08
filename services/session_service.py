"""
Session service for managing interview sessions.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str  # Fallback if email-validator not installed
from sqlalchemy.orm import Session as DBSession

from models import Session, get_db_context, SessionEvent
from config.constants import SessionStatus, UserType, EventType
from config.settings import settings
from utils.logger import logger


class SessionConfig(BaseModel):
    """Configuration for creating a new session."""
    
    candidate_name: str = Field(..., min_length=1, max_length=255)
    candidate_email: Optional[EmailStr] = None
    time_limit: int = Field(default=3600, gt=0, description="Time limit in seconds")
    token_budget: int = Field(default=50000, gt=0, description="Token budget")
    model_name: str = Field(default="gpt-4")
    challenge_id: Optional[str] = None
    challenge_text: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class SessionService:
    """Service for managing interview sessions."""
    
    def __init__(self):
        """Initialize session service."""
        pass
    
    def create_session(
        self,
        config: SessionConfig,
        db: Optional[DBSession] = None
    ) -> Session:
        """
        Create a new interview session.
        
        Args:
            config: Session configuration
            db: Database session (optional)
            
        Returns:
            Created Session object
        """
        if db:
            return self._create_session_with_db(config, db)
        
        with get_db_context() as db:
            return self._create_session_with_db(config, db)
    
    def _create_session_with_db(
        self,
        config: SessionConfig,
        db: DBSession
    ) -> Session:
        """Internal method to create session with database session."""
        # Create session
        session = Session(
            candidate_name=config.candidate_name,
            candidate_email=config.candidate_email,
            time_limit=config.time_limit,
            token_budget=config.token_budget,
            model_name=config.model_name,
            challenge_id=config.challenge_id,
            challenge_text=config.challenge_text,
            status=SessionStatus.CREATED,
            config=config.config or {}
        )
        
        db.add(session)
        db.flush()  # Get the session ID
        
        # Log session creation event
        event = SessionEvent(
            session_id=session.id,
            event_type=EventType.SESSION_CREATED,
            description=f"Session created for {config.candidate_name}",
            data={
                "time_limit": config.time_limit,
                "token_budget": config.token_budget,
                "model": config.model_name
            }
        )
        db.add(event)
        db.commit()
        
        logger.info(
            f"Created session {session.id} for {config.candidate_name} "
            f"(time: {config.time_limit}s, budget: {config.token_budget} tokens)"
        )
        
        return session
    
    def get_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Session object or None if not found
        """
        if db:
            return self._get_session_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._get_session_with_db(session_id, db)
    
    def _get_session_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Session]:
        """Internal method to get session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        return session
    
    def update_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None,
        **updates
    ) -> Optional[Session]:
        """
        Update a session.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            **updates: Fields to update
            
        Returns:
            Updated Session object or None if not found
        """
        if db:
            return self._update_session_with_db(session_id, db, **updates)
        
        with get_db_context() as db:
            return self._update_session_with_db(session_id, db, **updates)
    
    def _update_session_with_db(
        self,
        session_id: str,
        db: DBSession,
        **updates
    ) -> Optional[Session]:
        """Internal method to update session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found for update")
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Updated session {session_id}: {list(updates.keys())}")
        
        return session
    
    def start_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Session]:
        """
        Start a session (transition from CREATED to ACTIVE).
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Updated Session object or None if not found
        """
        if db:
            return self._start_session_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._start_session_with_db(session_id, db)
    
    def _start_session_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Session]:
        """Internal method to start session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        if session.status != SessionStatus.CREATED:
            logger.warning(
                f"Cannot start session {session_id}: "
                f"current status is {session.status}"
            )
            return session
        
        # Update session
        session.status = SessionStatus.ACTIVE
        session.start_time = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        # Log event
        event = SessionEvent(
            session_id=session_id,
            event_type=EventType.SESSION_STARTED,
            description="Session started"
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Started session {session_id}")
        
        return session
    
    def end_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Session]:
        """
        End a session (transition to COMPLETED).
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Updated Session object or None if not found
        """
        if db:
            return self._end_session_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._end_session_with_db(session_id, db)
    
    def _end_session_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Session]:
        """Internal method to end session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        # Update session
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        # Log event
        event = SessionEvent(
            session_id=session_id,
            event_type=EventType.SESSION_COMPLETED,
            description="Session completed",
            data={
                "duration": (session.end_time - session.start_time).total_seconds() if session.start_time else 0,
                "tokens_used": session.tokens_used,
                "message_count": session.message_count
            }
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Ended session {session_id}")
        
        return session
    
    def pause_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Session]:
        """
        Pause a session.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Updated Session object or None if not found
        """
        if db:
            return self._pause_session_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._pause_session_with_db(session_id, db)
    
    def _pause_session_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Session]:
        """Internal method to pause session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        if session.status != SessionStatus.ACTIVE:
            logger.warning(
                f"Cannot pause session {session_id}: "
                f"current status is {session.status}"
            )
            return session
        
        # Update session
        session.status = SessionStatus.PAUSED
        session.paused_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        # Log event
        event = SessionEvent(
            session_id=session_id,
            event_type=EventType.SESSION_PAUSED,
            description="Session paused"
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Paused session {session_id}")
        
        return session
    
    def resume_session(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[Session]:
        """
        Resume a paused session.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Updated Session object or None if not found
        """
        if db:
            return self._resume_session_with_db(session_id, db)
        
        with get_db_context() as db:
            return self._resume_session_with_db(session_id, db)
    
    def _resume_session_with_db(
        self,
        session_id: str,
        db: DBSession
    ) -> Optional[Session]:
        """Internal method to resume session with database session."""
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        if session.status != SessionStatus.PAUSED:
            logger.warning(
                f"Cannot resume session {session_id}: "
                f"current status is {session.status}"
            )
            return session
        
        # Calculate paused duration
        if session.paused_at:
            paused_duration = (datetime.utcnow() - session.paused_at).total_seconds()
            session.total_paused_duration += int(paused_duration)
        
        # Update session
        session.status = SessionStatus.ACTIVE
        session.paused_at = None
        session.updated_at = datetime.utcnow()
        
        # Log event
        event = SessionEvent(
            session_id=session_id,
            event_type=EventType.SESSION_RESUMED,
            description="Session resumed"
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Resumed session {session_id}")
        
        return session
    
    def validate_session_access(
        self,
        session_id: str,
        user_type: UserType,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Validate that a user can access a session.
        
        Args:
            session_id: Session ID
            user_type: Type of user (candidate or interviewer)
            db: Database session (optional)
            
        Returns:
            True if access is allowed, False otherwise
        """
        session = self.get_session(session_id, db)
        
        if not session:
            return False
        
        # For now, all users can access all sessions
        # In the future, this could check permissions, etc.
        return True
    
    def is_session_expired(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> bool:
        """
        Check if a session has expired based on time limit.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            True if expired, False otherwise
        """
        session = self.get_session(session_id, db)
        
        if not session:
            return True
        
        if session.status in [SessionStatus.COMPLETED, SessionStatus.EXPIRED]:
            return True
        
        if not session.start_time:
            return False
        
        # Calculate elapsed time (excluding paused duration)
        elapsed = (datetime.utcnow() - session.start_time).total_seconds()
        elapsed -= session.total_paused_duration
        
        # Add current pause duration if paused
        if session.status == SessionStatus.PAUSED and session.paused_at:
            elapsed -= (datetime.utcnow() - session.paused_at).total_seconds()
        
        return elapsed >= session.time_limit
    
    def get_remaining_time(
        self,
        session_id: str,
        db: Optional[DBSession] = None
    ) -> Optional[int]:
        """
        Get remaining time for a session in seconds.
        
        Args:
            session_id: Session ID
            db: Database session (optional)
            
        Returns:
            Remaining time in seconds, or None if session not found
        """
        session = self.get_session(session_id, db)
        
        if not session:
            return None
        
        if not session.start_time:
            return session.time_limit
        
        # Calculate elapsed time
        elapsed = (datetime.utcnow() - session.start_time).total_seconds()
        elapsed -= session.total_paused_duration
        
        # Add current pause duration if paused
        if session.status == SessionStatus.PAUSED and session.paused_at:
            elapsed -= (datetime.utcnow() - session.paused_at).total_seconds()
        
        remaining = session.time_limit - elapsed
        return max(0, int(remaining))
    
    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        limit: int = 50,
        offset: int = 0,
        db: Optional[DBSession] = None
    ) -> List[Session]:
        """
        List sessions with optional filtering.
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of sessions to return
            offset: Offset for pagination
            db: Database session (optional)
            
        Returns:
            List of Session objects
        """
        if db:
            return self._list_sessions_with_db(status, limit, offset, db)
        
        with get_db_context() as db:
            return self._list_sessions_with_db(status, limit, offset, db)
    
    def _list_sessions_with_db(
        self,
        status: Optional[SessionStatus],
        limit: int,
        offset: int,
        db: DBSession
    ) -> List[Session]:
        """Internal method to list sessions with database session."""
        query = db.query(Session)
        
        if status:
            query = query.filter(Session.status == status)
        
        sessions = query.order_by(Session.created_at.desc()).limit(limit).offset(offset).all()
        
        return sessions


# Global session service instance
_session_service = None


def get_session_service() -> SessionService:
    """Get global session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service

