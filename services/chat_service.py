"""
Chat service for handling message sending and conversation management.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session as DBSession
import logging

from models.models import Session, Message, SessionEvent
from models.database import get_db
from config.constants import MessageRole, SessionStatus, EventType
from config.settings import get_settings
from api.openai_client import OpenAIClient, get_openai_client
from utils.token_counter import TokenCounter, get_token_counter
from services.session_service import SessionService, get_session_service
from services.timer_service import get_timer_service

logger = logging.getLogger(__name__)


class ChatMessage:
    """Represents a chat message with metadata."""
    
    def __init__(
        self,
        role: MessageRole,
        content: str,
        tokens: int = 0,
        created_at: datetime = None
    ):
        self.role = role
        self.content = content
        self.tokens = tokens
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "role": self.role.value if isinstance(self.role, MessageRole) else self.role,
            "content": self.content,
            "tokens": self.tokens,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


class ChatService:
    """Service for managing chat interactions."""
    
    def __init__(self):
        self.settings = get_settings()
        self.token_counter = get_token_counter()
        self.session_service = get_session_service()
    
    def _validate_session(self, session: Session) -> Tuple[bool, Optional[str]]:
        """
        Validate session can accept new messages.
        
        Returns:
            (is_valid, error_message)
        """
        # Check session status
        if session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            return False, f"Session is {session.status.value}. Cannot send messages."
        
        # Check if session has started
        if not session.start_time:
            return False, "Session has not been started yet."
        
        # Check token budget
        if session.tokens_used >= session.token_budget:
            return False, "Token budget exhausted. Cannot send more messages."
        
        # Check time limit (if session is active)
        if session.status == SessionStatus.ACTIVE:
            timer_service = get_timer_service()
            if timer_service.is_expired(session):
                return False, "Session time has expired."
        
        return True, None
    
    def _create_system_message(self, session: Session) -> Dict[str, str]:
        """Create system message with interview context."""
        system_content = f"""You are an AI interviewer assistant helping a candidate with their coding interview.

Candidate: {session.candidate_name}
Time Limit: {session.time_limit // 60} minutes
Token Budget: {session.token_budget} tokens

"""
        
        if session.challenge_text:
            system_content += f"""Challenge:
{session.challenge_text}

"""
        
        system_content += """Guidelines:
- Provide helpful guidance without giving away complete solutions
- Ask clarifying questions to understand the candidate's approach
- Offer hints when the candidate is stuck
- Encourage the candidate to explain their thinking
- Help debug issues in their code
- Be supportive and constructive

Remember to track token usage and time limits."""
        
        return {"role": "system", "content": system_content}
    
    def format_messages_for_api(
        self,
        session_id: str,
        db: DBSession
    ) -> List[Dict[str, str]]:
        """
        Format all messages for OpenAI API call.
        
        Args:
            session_id: Session ID
            db: Database session
        
        Returns:
            List of message dictionaries in OpenAI format
        """
        # Get session
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Start with system message
        messages = [self._create_system_message(session)]
        
        # Add conversation history
        history = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).all()
        
        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return messages
    
    async def send_message(
        self,
        session_id: str,
        message_content: str,
        db: DBSession
    ) -> Tuple[bool, Optional[ChatMessage], Optional[str]]:
        """
        Send a message and get AI response.
        
        This is the main flow:
        1. Validate session
        2. Check token budget (pre-flight)
        3. Save user message
        4. Format messages for API
        5. Call OpenAI API
        6. Save AI response
        7. Update token consumption
        8. Update session statistics
        
        Args:
            session_id: Session ID
            message_content: User's message
            db: Database session
        
        Returns:
            (success, ai_message, error_message)
        """
        try:
            # Get session
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                return False, None, f"Session {session_id} not found"
            
            # Validate session
            is_valid, error_msg = self._validate_session(session)
            if not is_valid:
                logger.warning(f"Session validation failed for {session_id}: {error_msg}")
                return False, None, error_msg
            
            # Validate message length
            if len(message_content) > self.settings.max_message_length:
                return False, None, f"Message too long. Maximum {self.settings.max_message_length} characters."
            
            if not message_content.strip():
                return False, None, "Message cannot be empty."
            
            # Estimate tokens for the new message
            estimated_user_tokens = self.token_counter.count_tokens(
                message_content,
                session.model_name
            )
            
            # Reserve tokens (estimate for response too - rough estimate of 2x user tokens)
            estimated_total = estimated_user_tokens * 3  # User + estimated response
            remaining_budget = session.token_budget - session.tokens_used
            
            if estimated_total > remaining_budget:
                return False, None, f"Insufficient token budget. Need ~{estimated_total} tokens, have {remaining_budget}."
            
            # Save user message
            user_message = Message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content.strip(),
                tokens=estimated_user_tokens
            )
            db.add(user_message)
            db.commit()
            
            logger.info(f"User message saved for session {session_id}: {estimated_user_tokens} tokens")
            
            # Format messages for API
            api_messages = self.format_messages_for_api(session_id, db)
            
            # Get OpenAI client
            openai_client = get_openai_client()
            
            # Call OpenAI API
            logger.info(f"Calling OpenAI API for session {session_id}")
            response = await openai_client.chat_completion(
                messages=api_messages,
                model=session.model_name,
                temperature=self.settings.openai_temperature,
                max_tokens=min(
                    self.settings.openai_max_tokens,
                    remaining_budget - estimated_user_tokens
                )
            )
            
            # Extract response
            ai_content = response["choices"][0]["message"]["content"]
            
            # Get actual token usage from response
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            logger.info(f"OpenAI response received: {total_tokens} tokens (prompt: {prompt_tokens}, completion: {completion_tokens})")
            
            # Save AI message
            ai_message = Message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=ai_content,
                tokens=completion_tokens
            )
            db.add(ai_message)
            
            # Update session statistics
            session.tokens_used += total_tokens
            session.input_tokens += prompt_tokens
            session.output_tokens += completion_tokens
            session.message_count += 2  # User + AI
            session.updated_at = datetime.utcnow()
            
            # Log event
            event = SessionEvent(
                session_id=session_id,
                event_type=EventType.MESSAGE_SENT,
                description=f"Message exchange: {total_tokens} tokens used",
                data={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "message_count": session.message_count
                }
            )
            db.add(event)
            
            db.commit()
            
            logger.info(f"Chat exchange complete for session {session_id}: Total tokens used: {session.tokens_used}/{session.token_budget}")
            
            # Create response object
            response_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=ai_content,
                tokens=completion_tokens,
                created_at=ai_message.created_at
            )
            
            return True, response_message, None
            
        except Exception as e:
            logger.error(f"Error in send_message for session {session_id}: {e}", exc_info=True)
            db.rollback()
            return False, None, f"An error occurred: {str(e)}"
    
    def get_conversation(
        self,
        session_id: str,
        db: DBSession
    ) -> List[ChatMessage]:
        """
        Get full conversation history for a session.
        
        Args:
            session_id: Session ID
            db: Database session
        
        Returns:
            List of ChatMessage objects
        """
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).all()
        
        return [
            ChatMessage(
                role=msg.role,
                content=msg.content,
                tokens=msg.tokens,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    
    def get_message_count(self, session_id: str, db: DBSession) -> int:
        """Get total message count for a session."""
        return db.query(Message).filter(Message.session_id == session_id).count()


# Global service instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service

