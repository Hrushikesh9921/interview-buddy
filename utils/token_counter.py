"""
Token counting utilities using tiktoken.
Provides accurate token counting for OpenAI models.
"""
import tiktoken
from typing import List, Dict, Optional
from functools import lru_cache

from utils.logger import logger
from config.constants import TOKEN_LIMITS


class TokenCounter:
    """Token counter for OpenAI models using tiktoken."""
    
    def __init__(self):
        """Initialize token counter."""
        self._encodings = {}
    
    @lru_cache(maxsize=10)
    def get_encoding(self, model: str) -> tiktoken.Encoding:
        """
        Get encoding for a specific model with caching.
        
        Args:
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            
        Returns:
            tiktoken.Encoding instance
        """
        try:
            # Try to get encoding for the specific model
            encoding = tiktoken.encoding_for_model(model)
            logger.debug(f"Loaded encoding for model: {model}")
            return encoding
        except KeyError:
            # Fallback to cl100k_base encoding (used by gpt-4 and gpt-3.5-turbo)
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            return tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        Count tokens in a single text string.
        
        Args:
            text: Text to count tokens for
            model: Model name for encoding
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        try:
            encoding = self.get_encoding(model)
            tokens = encoding.encode(text)
            count = len(tokens)
            logger.debug(f"Counted {count} tokens for text of length {len(text)}")
            return count
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Rough estimation: ~4 characters per token
            return len(text) // 4
    
    def count_message_tokens(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4"
    ) -> int:
        """
        Count tokens in a list of chat messages.
        
        This accounts for the special tokens and formatting that OpenAI uses
        for chat completions.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name for encoding
            
        Returns:
            Total number of tokens including formatting
            
        Note:
            Token counting for chat messages includes:
            - Message content tokens
            - Role tokens
            - Special formatting tokens
            - System message overhead
        """
        if not messages:
            return 0
        
        try:
            encoding = self.get_encoding(model)
            
            # Token overhead per message varies by model
            if model.startswith("gpt-4"):
                tokens_per_message = 3
                tokens_per_name = 1
            elif model.startswith("gpt-3.5-turbo"):
                tokens_per_message = 4
                tokens_per_name = -1
            else:
                # Default to gpt-4 format
                tokens_per_message = 3
                tokens_per_name = 1
            
            num_tokens = 0
            
            for message in messages:
                num_tokens += tokens_per_message
                
                for key, value in message.items():
                    if value:
                        num_tokens += len(encoding.encode(str(value)))
                        if key == "name":
                            num_tokens += tokens_per_name
            
            # Every reply is primed with assistant tokens
            num_tokens += 3
            
            logger.debug(f"Counted {num_tokens} tokens for {len(messages)} messages")
            return num_tokens
            
        except Exception as e:
            logger.error(f"Error counting message tokens: {e}")
            # Rough estimation
            total_chars = sum(len(str(m.get('content', ''))) for m in messages)
            return total_chars // 4
    
    def estimate_completion_tokens(
        self, 
        prompt_tokens: int, 
        max_tokens: Optional[int] = None,
        model: str = "gpt-4"
    ) -> int:
        """
        Estimate completion tokens based on prompt and max_tokens.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            max_tokens: Maximum tokens for completion (None = model default)
            model: Model name
            
        Returns:
            Estimated completion tokens
        """
        if max_tokens:
            return min(max_tokens, TOKEN_LIMITS.get(model, 2000))
        
        # Default estimation: ~50% of prompt length, capped at reasonable limit
        estimated = min(prompt_tokens // 2, 500)
        return estimated
    
    def get_model_limit(self, model: str) -> int:
        """
        Get token limit for a model.
        
        Args:
            model: Model name
            
        Returns:
            Token limit for the model
        """
        return TOKEN_LIMITS.get(model, 4096)
    
    def check_token_limit(
        self, 
        prompt_tokens: int, 
        max_completion_tokens: int,
        model: str = "gpt-4"
    ) -> bool:
        """
        Check if prompt + completion fits within model limits.
        
        Args:
            prompt_tokens: Number of prompt tokens
            max_completion_tokens: Maximum completion tokens
            model: Model name
            
        Returns:
            True if within limits, False otherwise
        """
        total = prompt_tokens + max_completion_tokens
        limit = self.get_model_limit(model)
        
        if total > limit:
            logger.warning(
                f"Token count {total} exceeds model limit {limit} for {model}"
            )
            return False
        
        return True


# Global token counter instance
_token_counter = None


def get_token_counter() -> TokenCounter:
    """Get global token counter instance."""
    global _token_counter
    if _token_counter is None:
        _token_counter = TokenCounter()
    return _token_counter


# Convenience functions
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text."""
    return get_token_counter().count_tokens(text, model)


def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-4") -> int:
    """Count tokens in messages."""
    return get_token_counter().count_message_tokens(messages, model)


def check_token_limit(
    prompt_tokens: int, 
    max_completion_tokens: int,
    model: str = "gpt-4"
) -> bool:
    """Check if tokens fit within model limits."""
    return get_token_counter().check_token_limit(
        prompt_tokens, max_completion_tokens, model
    )

