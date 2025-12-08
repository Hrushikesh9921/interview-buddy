"""
Tests for OpenAI API client.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from openai import RateLimitError, APITimeoutError

from api.openai_client import OpenAIClient, get_openai_client


class TestOpenAIClient:
    """Test OpenAIClient class."""
    
    def test_client_initialization(self, test_settings):
        """Test client initialization."""
        client = OpenAIClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.client is not None
    
    def test_client_initialization_no_key(self):
        """Test client initialization without API key raises error."""
        with patch('api.openai_client.settings') as mock_settings:
            mock_settings.openai_api_key = ""
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                OpenAIClient()
    
    @pytest.mark.asyncio
    async def test_chat_completion_success(self):
        """Test successful chat completion."""
        client = OpenAIClient(api_key="test-key")
        
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 8
        mock_response.usage.total_tokens = 18
        mock_response.model = "gpt-4"
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        
        with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            messages = [{"role": "user", "content": "Hello!"}]
            result = await client.chat_completion(messages)
            
            assert result["content"] == "Hello! How can I help you?"
            assert result["usage"]["total_tokens"] == 18
            assert result["model"] == "gpt-4"
            assert result["finish_reason"] == "stop"
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_parameters(self):
        """Test chat completion with custom parameters."""
        client = OpenAIClient(api_key="test-key")
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.model = "gpt-3.5-turbo"
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        
        with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            messages = [{"role": "user", "content": "Test"}]
            result = await client.chat_completion(
                messages,
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=100
            )
            
            assert result is not None
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["model"] == "gpt-3.5-turbo"
            assert call_kwargs["temperature"] == 0.5
            assert call_kwargs["max_tokens"] == 100
    
    @pytest.mark.asyncio
    async def test_chat_completion_rate_limit_retry(self):
        """Test retry logic on rate limit error."""
        client = OpenAIClient(api_key="test-key")
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success after retry"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.model = "gpt-4"
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        
        with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # First call raises RateLimitError, second succeeds
            mock_create.side_effect = [
                RateLimitError("Rate limit exceeded", response=Mock(), body=None),
                mock_response
            ]
            
            messages = [{"role": "user", "content": "Test"}]
            result = await client.chat_completion(messages)
            
            assert result["content"] == "Success after retry"
            assert mock_create.call_count == 2
    
    @pytest.mark.asyncio
    async def test_chat_completion_max_retries_exceeded(self):
        """Test that max retries are respected."""
        client = OpenAIClient(api_key="test-key")
        
        with patch.object(client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # Always raise RateLimitError
            mock_create.side_effect = RateLimitError(
                "Rate limit exceeded", 
                response=Mock(), 
                body=None
            )
            
            messages = [{"role": "user", "content": "Test"}]
            
            with pytest.raises(RateLimitError):
                await client.chat_completion(messages)
            
            assert mock_create.call_count == 3  # max_retries
    
    def test_count_tokens_method(self):
        """Test count_tokens method."""
        client = OpenAIClient(api_key="test-key")
        
        tokens = client.count_tokens("Hello, world!")
        assert tokens > 0
        assert tokens < 10
    
    def test_count_message_tokens_method(self):
        """Test count_message_tokens method."""
        client = OpenAIClient(api_key="test-key")
        
        messages = [{"role": "user", "content": "Hello!"}]
        tokens = client.count_message_tokens(messages)
        assert tokens > 0


class TestOpenAIClientGlobal:
    """Test global OpenAI client functions."""
    
    def test_get_openai_client(self):
        """Test getting global client instance."""
        with patch('api.openai_client.settings') as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_temperature = 0.7
            mock_settings.openai_max_tokens = 2000
            
            client1 = get_openai_client()
            client2 = get_openai_client()
            
            # Should return same instance
            assert client1 is client2

