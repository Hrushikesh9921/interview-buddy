"""
Application-wide constants and enumerations.
"""
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration."""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MessageRole(str, Enum):
    """Message role enumeration."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class UserType(str, Enum):
    """User type enumeration."""
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"


class ChallengeCategory(str, Enum):
    """Challenge category enumeration."""
    ALGORITHMS = "algorithms"
    DATA_STRUCTURES = "data_structures"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    OTHER = "other"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TimerState(str, Enum):
    """Timer state enumeration."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    EXPIRED = "expired"


class EventType(str, Enum):
    """Session event type enumeration."""
    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_COMPLETED = "session_completed"
    SESSION_EXPIRED = "session_expired"
    TIME_EXTENDED = "time_extended"
    TOKENS_EXTENDED = "tokens_extended"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"


# Token limits by model
TOKEN_LIMITS = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-turbo": 128000,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
}

# Default system prompts
DEFAULT_INTERVIEWER_PROMPT = """You are an AI interview assistant helping candidates solve technical challenges. 
Be helpful, clear, and encouraging. Guide candidates toward solutions without giving direct answers.
Focus on understanding their thought process and helping them learn."""

# UI Constants
COLORS = {
    "primary": "#1f77b4",
    "success": "#2ca02c",
    "warning": "#ff7f0e",
    "danger": "#d62728",
    "info": "#17becf",
}

# Resource warning thresholds (percentages)
RESOURCE_THRESHOLDS = {
    "green": 50,  # > 50% remaining
    "yellow": 25,  # 25-50% remaining
    "orange": 10,  # 10-25% remaining
    "red": 10,  # < 10% remaining
}

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Export formats
EXPORT_FORMATS = ["markdown", "json", "pdf"]

# File size limits
MAX_UPLOAD_SIZE_MB = 10

