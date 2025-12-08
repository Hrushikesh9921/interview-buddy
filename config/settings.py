"""
Application settings and configuration management.
Loads environment variables and provides application-wide settings.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=2000, description="Max tokens per response")
    openai_temperature: float = Field(default=0.7, description="Temperature for responses")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/interview_buddy.db",
        description="Database connection URL"
    )
    
    # Application Configuration
    app_name: str = Field(default="Interview Buddy", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Session Configuration
    default_session_duration: int = Field(
        default=3600,
        description="Default session duration in seconds"
    )
    default_token_budget: int = Field(
        default=50000,
        description="Default token budget per session"
    )
    max_message_length: int = Field(
        default=5000,
        description="Maximum message length"
    )
    
    # Rate Limiting
    rate_limit_per_session: int = Field(
        default=100,
        description="Rate limit per session"
    )
    global_rate_limit: int = Field(
        default=1000,
        description="Global rate limit per hour"
    )
    
    # Timer Configuration
    timer_update_interval: int = Field(
        default=1,
        description="Timer update interval in seconds"
    )
    timer_warning_thresholds: str = Field(
        default="25,10,5",
        description="Timer warning thresholds as comma-separated percentages"
    )
    
    # Security
    secret_key: str = Field(
        default="change_this_to_a_random_secret_key",
        description="Secret key for security"
    )
    session_timeout: int = Field(
        default=86400,
        description="Session timeout in seconds"
    )
    
    # Frontend Configuration
    auto_refresh_interval: int = Field(
        default=2,
        description="Auto-refresh interval in seconds"
    )
    enable_markdown_rendering: bool = Field(
        default=True,
        description="Enable markdown rendering"
    )
    enable_code_highlighting: bool = Field(
        default=True,
        description="Enable code highlighting"
    )
    
    @property
    def warning_thresholds(self) -> list[int]:
        """Parse timer warning thresholds."""
        return [int(t.strip()) for t in self.timer_warning_thresholds.split(",")]
    
    @property
    def database_path(self) -> Path:
        """Get the database file path."""
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
            return PROJECT_ROOT / db_path
        return None
    
    def validate_openai_key(self) -> bool:
        """Validate that OpenAI API key is set."""
        return bool(self.openai_api_key and self.openai_api_key != "")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings

