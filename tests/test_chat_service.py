"""
Tests for Chat Service.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from services.chat_service import ChatService, ChatMessage, get_chat_service
from models.models import Session, Message
from config.constants import MessageRole, SessionStatus


@pytest.fixture
def chat_service():
    """Create a chat service instance."""
    return ChatService()


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = Mock(spec=Session)
    session.id = "test-session-123"
    session.candidate_name = "Test Candidate"
    session.time_limit = 3600
    session.token_budget = 10000
    session.tokens_used = 0
    session.input_tokens = 0
    session.output_tokens = 0
    session.message_count = 0
    session.model_name = "gpt-4"
    session.challenge_text = "Solve the two-sum problem"
    session.status = SessionStatus.ACTIVE
    session.start_time = datetime.utcnow()
    return session


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    return db


class TestChatService:
    """Test chat service functionality."""
    
    def test_get_chat_service(self):
        """Test getting global chat service instance."""
        service1 = get_chat_service()
        service2 = get_chat_service()
        assert service1 is service2  # Should be singleton
    
    def test_chat_message_creation(self):
        """Test ChatMessage creation."""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Test message",
            tokens=10
        )
        
        assert msg.role == MessageRole.USER
        assert msg.content == "Test message"
        assert msg.tokens == 10
        assert msg.created_at is not None
    
    def test_chat_message_to_dict(self):
        """Test ChatMessage to_dict conversion."""
        msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="AI response",
            tokens=20
        )
        
        msg_dict = msg.to_dict()
        
        assert isinstance(msg_dict, dict)
        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "AI response"
        assert msg_dict["tokens"] == 20
        assert "created_at" in msg_dict
    
    def test_validate_session_success(self, chat_service, mock_session):
        """Test session validation for valid session."""
        with patch.object(chat_service.session_service, 'is_session_expired', return_value=False):
            is_valid, error = chat_service._validate_session(mock_session)
            
            assert is_valid
            assert error is None
    
    def test_validate_session_not_started(self, chat_service, mock_session):
        """Test session validation for not started session."""
        mock_session.start_time = None
        
        is_valid, error = chat_service._validate_session(mock_session)
        
        assert not is_valid
        assert "not been started" in error
    
    def test_validate_session_completed(self, chat_service, mock_session):
        """Test session validation for completed session."""
        mock_session.status = SessionStatus.COMPLETED
        
        is_valid, error = chat_service._validate_session(mock_session)
        
        assert not is_valid
        assert "completed" in error.lower()
    
    def test_validate_session_token_budget_exhausted(self, chat_service, mock_session):
        """Test session validation when token budget is exhausted."""
        mock_session.tokens_used = 10000
        mock_session.token_budget = 10000
        
        is_valid, error = chat_service._validate_session(mock_session)
        
        assert not is_valid
        assert "Token budget exhausted" in error
    
    def test_create_system_message(self, chat_service, mock_session):
        """Test system message creation."""
        system_msg = chat_service._create_system_message(mock_session)
        
        assert system_msg["role"] == "system"
        assert "Test Candidate" in system_msg["content"]
        assert "60 minutes" in system_msg["content"]
        assert "Solve the two-sum problem" in system_msg["content"]
    
    def test_format_messages_for_api(self, chat_service, mock_session, mock_db):
        """Test formatting messages for OpenAI API."""
        # Mock database query
        mock_messages = [
            Mock(role=MessageRole.USER, content="Hello", created_at=datetime.utcnow()),
            Mock(role=MessageRole.ASSISTANT, content="Hi there!", created_at=datetime.utcnow())
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_messages
        mock_db.query.return_value = mock_query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        messages = chat_service.format_messages_for_api("test-session-123", mock_db)
        
        assert len(messages) == 3  # System + 2 messages
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Hi there!"
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, chat_service, mock_session, mock_db):
        """Test successful message sending."""
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        # Mock OpenAI client
        mock_openai_response = {
            "choices": [{
                "message": {
                    "content": "This is an AI response"
                }
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            }
        }
        
        with patch('services.chat_service.get_openai_client') as mock_get_client, \
             patch.object(chat_service.session_service, 'is_session_expired', return_value=False):
            mock_client = AsyncMock()
            mock_client.chat_completion = AsyncMock(return_value=mock_openai_response)
            mock_get_client.return_value = mock_client
            
            success, ai_message, error = await chat_service.send_message(
                "test-session-123",
                "Hello AI",
                mock_db
            )
        
        assert success
        assert ai_message is not None
        assert ai_message.content == "This is an AI response"
        assert ai_message.tokens == 30
        assert error is None
        
        # Verify database operations
        assert mock_db.add.call_count == 3  # user message, ai message, event
        assert mock_db.commit.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_send_message_empty(self, chat_service, mock_session, mock_db):
        """Test sending empty message."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        with patch.object(chat_service.session_service, 'is_session_expired', return_value=False):
            success, ai_message, error = await chat_service.send_message(
                "test-session-123",
                "   ",
                mock_db
            )
        
        assert not success
        assert ai_message is None
        assert "cannot be empty" in error
    
    @pytest.mark.asyncio
    async def test_send_message_too_long(self, chat_service, mock_session, mock_db):
        """Test sending message that's too long."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        long_message = "x" * 6000  # Exceeds default max length
        
        with patch.object(chat_service.session_service, 'is_session_expired', return_value=False):
            success, ai_message, error = await chat_service.send_message(
                "test-session-123",
                long_message,
                mock_db
            )
        
        assert not success
        assert ai_message is None
        assert "too long" in error
    
    @pytest.mark.asyncio
    async def test_send_message_insufficient_tokens(self, chat_service, mock_session, mock_db):
        """Test sending message with insufficient token budget."""
        mock_session.tokens_used = 9990
        mock_session.token_budget = 10000
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        with patch.object(chat_service.session_service, 'is_session_expired', return_value=False):
            success, ai_message, error = await chat_service.send_message(
                "test-session-123",
                "This is a very long message that will require many tokens to process",
                mock_db
            )
        
        assert not success
        assert ai_message is None
        assert "Insufficient token budget" in error
    
    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self, chat_service, mock_db):
        """Test sending message to non-existent session."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        success, ai_message, error = await chat_service.send_message(
            "non-existent-session",
            "Hello",
            mock_db
        )
        
        assert not success
        assert ai_message is None
        assert "not found" in error
    
    def test_get_conversation(self, chat_service, mock_db):
        """Test getting conversation history."""
        # Mock messages
        mock_messages = [
            Mock(
                role=MessageRole.USER,
                content="Hello",
                tokens=5,
                created_at=datetime.utcnow()
            ),
            Mock(
                role=MessageRole.ASSISTANT,
                content="Hi!",
                tokens=3,
                created_at=datetime.utcnow()
            )
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_messages
        mock_db.query.return_value = mock_query
        
        conversation = chat_service.get_conversation("test-session-123", mock_db)
        
        assert len(conversation) == 2
        assert conversation[0].role == MessageRole.USER
        assert conversation[0].content == "Hello"
        assert conversation[1].role == MessageRole.ASSISTANT
        assert conversation[1].content == "Hi!"
    
    def test_get_message_count(self, chat_service, mock_db):
        """Test getting message count."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 10
        mock_db.query.return_value = mock_query
        
        count = chat_service.get_message_count("test-session-123", mock_db)
        
        assert count == 10

