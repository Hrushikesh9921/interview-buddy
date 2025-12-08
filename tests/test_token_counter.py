"""
Tests for token counting utility.
"""
import pytest
from utils.token_counter import (
    TokenCounter,
    get_token_counter,
    count_tokens,
    count_message_tokens,
    check_token_limit
)


class TestTokenCounter:
    """Test TokenCounter class."""
    
    def test_token_counter_initialization(self):
        """Test token counter initialization."""
        counter = TokenCounter()
        assert counter is not None
        assert counter._encodings == {}
    
    def test_get_encoding(self):
        """Test getting encoding for a model."""
        counter = TokenCounter()
        encoding = counter.get_encoding("gpt-4")
        assert encoding is not None
        
        # Test caching
        encoding2 = counter.get_encoding("gpt-4")
        assert encoding == encoding2
    
    def test_get_encoding_unknown_model(self):
        """Test getting encoding for unknown model falls back to cl100k_base."""
        counter = TokenCounter()
        encoding = counter.get_encoding("unknown-model")
        assert encoding is not None
    
    def test_count_tokens_simple(self):
        """Test counting tokens in simple text."""
        counter = TokenCounter()
        
        # Simple text
        text = "Hello, world!"
        tokens = counter.count_tokens(text)
        assert tokens > 0
        assert tokens < 10  # Should be around 3-4 tokens
    
    def test_count_tokens_empty(self):
        """Test counting tokens in empty text."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0
        assert counter.count_tokens(None) == 0
    
    def test_count_tokens_long_text(self):
        """Test counting tokens in longer text."""
        counter = TokenCounter()
        
        text = "This is a longer piece of text that should have more tokens. " * 10
        tokens = counter.count_tokens(text)
        assert tokens > 50  # Should be substantial
    
    def test_count_message_tokens_single(self):
        """Test counting tokens in a single message."""
        counter = TokenCounter()
        
        messages = [
            {"role": "user", "content": "Hello!"}
        ]
        
        tokens = counter.count_message_tokens(messages)
        assert tokens > 0
        assert tokens < 20  # Should include message overhead
    
    def test_count_message_tokens_conversation(self):
        """Test counting tokens in a conversation."""
        counter = TokenCounter()
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi! How can I help you?"},
            {"role": "user", "content": "What's the weather like?"}
        ]
        
        tokens = counter.count_message_tokens(messages)
        assert tokens > 20  # Should be substantial with overhead
    
    def test_count_message_tokens_empty(self):
        """Test counting tokens in empty messages."""
        counter = TokenCounter()
        assert counter.count_message_tokens([]) == 0
    
    def test_count_message_tokens_different_models(self):
        """Test counting tokens for different models."""
        counter = TokenCounter()
        
        messages = [{"role": "user", "content": "Hello!"}]
        
        tokens_gpt4 = counter.count_message_tokens(messages, "gpt-4")
        tokens_gpt35 = counter.count_message_tokens(messages, "gpt-3.5-turbo")
        
        # Both should return valid counts (might differ slightly)
        assert tokens_gpt4 > 0
        assert tokens_gpt35 > 0
    
    def test_estimate_completion_tokens(self):
        """Test estimating completion tokens."""
        counter = TokenCounter()
        
        # With max_tokens
        estimated = counter.estimate_completion_tokens(100, max_tokens=50)
        assert estimated == 50
        
        # Without max_tokens (should estimate based on prompt)
        estimated = counter.estimate_completion_tokens(100)
        assert estimated > 0
        assert estimated <= 500
    
    def test_get_model_limit(self):
        """Test getting model token limits."""
        counter = TokenCounter()
        
        limit_gpt4 = counter.get_model_limit("gpt-4")
        assert limit_gpt4 == 8192
        
        limit_gpt35 = counter.get_model_limit("gpt-3.5-turbo")
        assert limit_gpt35 == 4096
        
        # Unknown model should return default
        limit_unknown = counter.get_model_limit("unknown")
        assert limit_unknown == 4096
    
    def test_check_token_limit_within(self):
        """Test checking token limit when within limits."""
        counter = TokenCounter()
        
        # Well within limits
        result = counter.check_token_limit(1000, 1000, "gpt-4")
        assert result is True
    
    def test_check_token_limit_exceeds(self):
        """Test checking token limit when exceeding limits."""
        counter = TokenCounter()
        
        # Exceeds limits
        result = counter.check_token_limit(8000, 1000, "gpt-4")
        assert result is False


class TestTokenCounterGlobalFunctions:
    """Test global token counter functions."""
    
    def test_get_token_counter(self):
        """Test getting global token counter instance."""
        counter1 = get_token_counter()
        counter2 = get_token_counter()
        
        # Should return same instance
        assert counter1 is counter2
    
    def test_count_tokens_function(self):
        """Test global count_tokens function."""
        tokens = count_tokens("Hello, world!")
        assert tokens > 0
        assert tokens < 10
    
    def test_count_message_tokens_function(self):
        """Test global count_message_tokens function."""
        messages = [{"role": "user", "content": "Hello!"}]
        tokens = count_message_tokens(messages)
        assert tokens > 0
    
    def test_check_token_limit_function(self):
        """Test global check_token_limit function."""
        result = check_token_limit(1000, 1000, "gpt-4")
        assert result is True
        
        result = check_token_limit(8000, 1000, "gpt-4")
        assert result is False


class TestTokenCountingAccuracy:
    """Test token counting accuracy."""
    
    def test_token_count_consistency(self):
        """Test that token counting is consistent."""
        text = "This is a test message for token counting."
        
        count1 = count_tokens(text)
        count2 = count_tokens(text)
        
        assert count1 == count2
    
    def test_message_token_count_consistency(self):
        """Test that message token counting is consistent."""
        messages = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        count1 = count_message_tokens(messages)
        count2 = count_message_tokens(messages)
        
        assert count1 == count2
    
    def test_token_count_scales_with_length(self):
        """Test that token count increases with text length."""
        short_text = "Hello"
        long_text = "Hello " * 100
        
        short_count = count_tokens(short_text)
        long_count = count_tokens(long_text)
        
        assert long_count > short_count
        assert long_count > short_count * 50  # Should be significantly more

