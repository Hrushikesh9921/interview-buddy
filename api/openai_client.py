"""
OpenAI API client with error handling and retry logic.
"""
import asyncio
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI, OpenAIError, RateLimitError, APITimeoutError
import time

from config.settings import settings
from utils.logger import logger
from utils.token_counter import count_tokens, count_message_tokens


class OpenAIClient:
    """
    OpenAI API client with error handling, retry logic, and token counting.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = settings.openai_model
        self.default_temperature = settings.openai_temperature
        self.default_max_tokens = settings.openai_max_tokens
        
        logger.info(f"Initialized OpenAI client with model: {self.default_model}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion with error handling and retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API
            
        Returns:
            Dict containing:
                - content: The completion text
                - usage: Token usage information
                - model: Model used
                - finish_reason: Why the completion finished
                
        Raises:
            OpenAIError: If API call fails after retries
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        # Count input tokens
        input_tokens = count_message_tokens(messages, model)
        logger.info(f"Sending request with {input_tokens} input tokens")
        
        # Retry configuration
        max_retries = 3
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs
                )
                
                if stream:
                    # Return the stream directly for streaming responses
                    return response
                
                # Extract response data
                completion = response.choices[0]
                content = completion.message.content
                usage = response.usage
                
                result = {
                    "content": content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    },
                    "model": response.model,
                    "finish_reason": completion.finish_reason,
                    "id": response.id,
                    "created": response.created
                }
                
                logger.info(
                    f"Completion successful: {usage.total_tokens} tokens "
                    f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})"
                )
                
                return result
                
            except RateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max retries reached for rate limit")
                    raise
                    
            except APITimeoutError as e:
                logger.warning(f"API timeout (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max retries reached for timeout")
                    raise
                    
            except OpenAIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error in chat completion: {e}", exc_info=True)
                raise
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Stream a chat completion.
        
        Args:
            messages: List of message dicts
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the completion as they arrive
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in streaming completion: {e}", exc_info=True)
            raise
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            model: Model to use for counting
            
        Returns:
            Number of tokens
        """
        model = model or self.default_model
        return count_tokens(text, model)
    
    def count_message_tokens(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None
    ) -> int:
        """
        Count tokens in messages.
        
        Args:
            messages: List of message dicts
            model: Model to use for counting
            
        Returns:
            Number of tokens
        """
        model = model or self.default_model
        return count_message_tokens(messages, model)
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a minimal API call.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            await self.chat_completion(
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            logger.info("API key validation successful")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False


# Global client instance
_openai_client = None


def get_openai_client() -> OpenAIClient:
    """Get global OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client

