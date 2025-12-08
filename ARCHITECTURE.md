# Interview Buddy - Technical Architecture Document

## Executive Summary

Interview Buddy is an AI-powered interview assessment platform built with Python and Streamlit. The system enforces strict resource constraints (time and tokens) to evaluate candidates' ability to solve technical challenges using AI assistance efficiently. This document provides comprehensive technical architecture, implementation details, API specifications, and deployment strategies.

## 1. Project Overview

### 1.1 Purpose
Interview Buddy enables interviewers to evaluate candidates':
- Problem-solving skills with AI assistance
- Ability to work under time pressure
- Resource management (token usage)
- Efficiency in leveraging AI tools
- Understanding of AI limitations and best practices

### 1.2 Core Concept
Candidates are given a challenge/problem and access to an AI chatbot (ChatGPT-powered) with:
- **Time Limit**: Fixed duration (e.g., 30-60 minutes)
- **Token Budget**: Limited API tokens (e.g., 10,000-50,000 tokens)
- **Real-time Monitoring**: Both limits visible to candidate and interviewer
- **Automatic Enforcement**: System stops when either limit is reached

### 1.3 Key Improvements to Original Idea

1. **Dual-Mode Interface**
   - Candidate view: Clean chat interface with timer/token counter
   - Interviewer dashboard: Real-time monitoring, session analytics, ability to extend limits if needed

2. **Session Management**
   - Pre-configured interview sessions with customizable limits
   - Session history and replay capability
   - Export conversation logs for review

3. **Enhanced Monitoring**
   - Real-time token consumption tracking
   - Token usage breakdown (input vs output)
   - Estimated remaining queries based on current usage pattern
   - Warning alerts at 75% and 90% thresholds

4. **Challenge Templates**
   - Pre-built challenge/problem templates
   - Ability to upload custom challenges
   - Challenge difficulty levels

5. **Analytics & Insights**
   - Token efficiency metrics
   - Time utilization analysis
   - Conversation quality indicators
   - Candidate performance summary

6. **Safety Features**
   - Rate limiting to prevent API abuse
   - Conversation sanitization
   - Session timeout handling
   - Graceful degradation when limits reached

## 2. Functional Requirements

### 2.1 Core Features

#### 2.1.1 Chat Interface
- **ChatGPT-like UI**: Clean, modern chat interface
- **Message History**: Persistent conversation with scrollable history
- **Message Types**: User messages, AI responses, system notifications
- **Markdown Support**: Code blocks, formatted text rendering
- **Copy/Export**: Ability to copy messages or export entire conversation

#### 2.1.2 Timer System
- **Countdown Timer**: Visible countdown from set time limit
- **Time Remaining Display**: Clear indication of remaining time
- **Warning States**: Visual warnings at 25%, 10%, and 5% remaining
- **Auto-Stop**: Chat disabled when timer reaches zero
- **Pause/Resume**: Optional pause functionality (configurable by interviewer)

#### 2.1.3 Token Management
- **Real-time Counter**: Live token consumption display
- **Token Breakdown**: Input tokens, output tokens, total tokens
- **Budget Display**: Remaining tokens vs. total budget
- **Usage Graph**: Visual representation of token consumption over time
- **Per-Message Tracking**: Token count for each message/response
- **Auto-Stop**: Chat disabled when token budget exhausted

#### 2.1.4 Session Management
- **Session Creation**: Interviewer creates session with configurable parameters
- **Session ID**: Unique identifier for each interview session
- **Session State**: Active, paused, completed, expired
- **Session Persistence**: Save and resume sessions
- **Session History**: View past sessions

#### 2.1.5 Challenge Management
- **Challenge Library**: Pre-built challenge templates
- **Custom Challenges**: Upload/enter custom problems
- **Challenge Metadata**: Title, description, difficulty, expected time
- **Challenge Attachments**: Support for files, images, code snippets

### 2.2 Interviewer Features

#### 2.2.1 Dashboard
- **Active Sessions**: Monitor all active interview sessions
- **Session Details**: View timer, tokens, conversation in real-time
- **Control Panel**: Extend time/tokens, pause/resume, end session
- **Analytics**: Session statistics and insights

#### 2.2.2 Session Configuration
- **Time Limits**: Set duration (15 min to 2 hours)
- **Token Budgets**: Configure token limits (1K to 100K tokens)
- **Model Selection**: Choose GPT model (gpt-3.5-turbo, gpt-4, etc.)
- **Temperature Settings**: Configure AI creativity/consistency
- **System Prompts**: Customize AI behavior/instructions

#### 2.2.3 Post-Interview Analysis
- **Conversation Export**: Download full conversation logs
- **Performance Metrics**: Token efficiency, time utilization
- **Quality Indicators**: Response relevance, code quality (if applicable)
- **Comparison Tools**: Compare multiple candidates

### 2.3 Candidate Features

#### 2.3.1 Chat Interface
- **Clean UI**: Distraction-free chat interface
- **Resource Awareness**: Always-visible timer and token counter
- **Status Indicators**: Clear indication of remaining resources
- **Error Handling**: Graceful error messages for API failures

#### 2.3.2 Challenge View
- **Problem Display**: Clear presentation of challenge/problem
- **Context Preservation**: Challenge visible throughout session
- **Resource Constraints**: Clear indication of limits

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Presentation Layer (Streamlit)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Candidate   │  │ Interviewer  │  │   Admin      │      │
│  │    View      │  │  Dashboard   │  │   Panel      │      │
│  │  (Pages)     │  │  (Pages)     │  │  (Pages)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         Shared Components & State Management         │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Service Layer (Python)               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Business Logic Services                  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │    │
│  │  │   Session    │  │   Token      │  │   Timer  │  │    │
│  │  │  Service     │  │   Service    │  │  Service │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │    │
│  │  │   Chat       │  │   Challenge  │  │ Analytics │  │    │
│  │  │   Service    │  │   Service    │  │  Service │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Background Workers                        │    │
│  │  ┌──────────────┐  ┌──────────────┐                  │    │
│  │  │   Timer      │  │   Cleanup    │                  │    │
│  │  │   Worker     │  │   Worker     │                  │    │
│  │  └──────────────┘  └──────────────┘                  │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              External API Integration Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   OpenAI     │  │   Rate       │  │   Error      │      │
│  │   Client     │  │   Limiter    │  │   Handler    │      │
│  │  (Async)     │  │  (Redis)     │  │  (Retry)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Token      │  │   Cache      │                        │
│  │   Counter    │  │   Manager    │                        │
│  │  (Tiktoken)   │  │  (Redis)     │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │   Cache      │  │   File       │      │
│  │  (PostgreSQL)│  │   (Redis)    │  │   Storage    │      │
│  │              │  │              │  │   (S3/Local)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              ORM Layer (SQLAlchemy)                   │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3.1.1 Architecture Patterns

**Layered Architecture**
- **Presentation Layer**: Streamlit pages and components
- **Service Layer**: Business logic and orchestration
- **Integration Layer**: External API clients and adapters
- **Data Layer**: Database access and caching

**Service-Oriented Design**
- Each service handles a specific domain (Session, Token, Timer, Chat, etc.)
- Services communicate through well-defined interfaces
- Dependency injection for testability
- Async/await for I/O-bound operations

**Event-Driven Components**
- Timer service publishes time events
- Token service publishes consumption events
- Analytics service subscribes to events
- Enables real-time updates and decoupling

### 3.2 Component Architecture

#### 3.2.1 Frontend Components (Streamlit)

**Page Structure**
```
app.py (Main Entry)
├── pages/
│   ├── candidate.py          # Candidate chat interface
│   ├── interviewer.py         # Interviewer dashboard
│   ├── session_create.py      # Session creation form
│   ├── session_history.py     # Historical sessions view
│   └── analytics.py          # Analytics dashboard
```

**Candidate Interface Components**
- `components/candidate/resource_panel.py`: 
  - Timer display with countdown
  - Token counter with progress bars
  - Warning indicators
  - Auto-refresh mechanism
  
- `components/candidate/chat_interface.py`:
  - Message input with validation
  - Message history rendering
  - Markdown code block rendering
  - Token estimation preview
  
- `components/candidate/challenge_display.py`:
  - Collapsible challenge panel
  - Syntax-highlighted code blocks
  - Challenge metadata display

**Interviewer Dashboard Components**
- `components/interviewer/session_list.py`:
  - Active sessions grid
  - Session status indicators
  - Quick action buttons
  
- `components/interviewer/session_monitor.py`:
  - Live conversation feed
  - Real-time metrics display
  - Control panel (pause/resume/extend/end)
  
- `components/interviewer/analytics_charts.py`:
  - Token usage graphs (Plotly)
  - Time utilization charts
  - Performance metrics cards

**Shared Components**
- `components/shared/session_state.py`:
  - Streamlit session state management
  - State persistence helpers
  - State validation
  
- `components/shared/message_renderer.py`:
  - Markdown rendering
  - Code syntax highlighting
  - Token badge display
  
- `components/shared/styles.py`:
  - Custom CSS injection
  - Theme configuration
  - Responsive design helpers

#### 3.2.2 Backend Service Layer

**Core Services Implementation**

**Session Service** (`services/session_service.py`)
```python
class SessionService:
    def create_session(config: SessionConfig) -> Session
    def get_session(session_id: str) -> Session
    def update_session(session_id: str, updates: dict) -> Session
    def pause_session(session_id: str) -> Session
    def resume_session(session_id: str) -> Session
    def end_session(session_id: str) -> Session
    def extend_time(session_id: str, additional_seconds: int) -> Session
    def extend_tokens(session_id: str, additional_tokens: int) -> Session
    def get_active_sessions(interviewer_id: str) -> List[Session]
    def validate_session_access(session_id: str, user_type: str) -> bool
```

**Token Service** (`services/token_service.py`)
```python
class TokenService:
    def estimate_tokens(text: str, model: str) -> int
    def reserve_tokens(session_id: str, estimated: int) -> bool
    def update_consumption(session_id: str, input_tokens: int, 
                          output_tokens: int) -> TokenUsage
    def get_remaining_budget(session_id: str) -> int
    def check_budget(session_id: str, estimated: int) -> bool
    def get_token_breakdown(session_id: str) -> TokenBreakdown
    def get_usage_history(session_id: str) -> List[TokenUsage]
```

**Timer Service** (`services/timer_service.py`)
```python
class TimerService:
    def start_timer(session_id: str, duration_seconds: int) -> Timer
    def pause_timer(session_id: str) -> Timer
    def resume_timer(session_id: str) -> Timer
    def get_remaining_time(session_id: str) -> int
    def extend_timer(session_id: str, additional_seconds: int) -> Timer
    def is_expired(session_id: str) -> bool
    def get_timer_state(session_id: str) -> TimerState
    # Background worker
    def _timer_worker() -> None  # Runs in separate thread
```

**Chat Service** (`services/chat_service.py`)
```python
class ChatService:
    async def send_message(session_id: str, message: str) -> Message
    def get_conversation(session_id: str) -> List[Message]
    def format_messages_for_api(session_id: str) -> List[dict]
    def add_system_message(session_id: str, content: str) -> Message
    def export_conversation(session_id: str, format: str) -> bytes
```

**Challenge Service** (`services/challenge_service.py`)
```python
class ChallengeService:
    def create_challenge(challenge_data: ChallengeData) -> Challenge
    def get_challenge(challenge_id: str) -> Challenge
    def list_challenges(filters: dict) -> List[Challenge]
    def update_challenge(challenge_id: str, updates: dict) -> Challenge
    def delete_challenge(challenge_id: str) -> bool
    def get_challenge_templates() -> List[Challenge]
```

**Analytics Service** (`services/analytics_service.py`)
```python
class AnalyticsService:
    def calculate_efficiency_metrics(session_id: str) -> EfficiencyMetrics
    def generate_performance_report(session_id: str) -> PerformanceReport
    def compare_sessions(session_ids: List[str]) -> ComparisonReport
    def get_token_usage_timeline(session_id: str) -> List[DataPoint]
    def get_time_utilization(session_id: str) -> TimeUtilization
    def calculate_quality_score(session_id: str) -> QualityScore
```

#### 3.2.3 API Integration Layer

**OpenAI Client** (`api/openai_client.py`)
```python
class OpenAIClient:
    def __init__(api_key: str, base_url: str = None)
    async def chat_completion(
        messages: List[dict],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> ChatCompletionResponse
    def count_tokens(text: str, model: str) -> int
    def get_model_info(model: str) -> ModelInfo
```

**Rate Limiter** (`api/rate_limiter.py`)
```python
class RateLimiter:
    def __init__(redis_client: Redis)
    def check_rate_limit(session_id: str, limit: int, window: int) -> bool
    def get_remaining_requests(session_id: str) -> int
    def reset_rate_limit(session_id: str) -> None
```

**Error Handler** (`api/error_handler.py`)
```python
class ErrorHandler:
    @retry(max_attempts=3, backoff=exponential)
    async def handle_api_call(callable_func) -> Any
    def handle_rate_limit_error(error: RateLimitError) -> None
    def handle_api_error(error: APIError) -> None
    def get_user_friendly_message(error: Exception) -> str
```

#### 3.2.4 Data Models

**SQLAlchemy Models** (`models/models.py`)
```python
class Session(Base):
    id: str (UUID, Primary Key)
    interviewer_id: str
    candidate_name: str
    candidate_email: str
    challenge_id: str (Foreign Key)
    time_limit: int
    token_budget: int
    tokens_used: int
    start_time: datetime
    end_time: datetime
    status: str (Enum: active, paused, completed, expired)
    model_name: str
    system_prompt: str
    temperature: float
    created_at: datetime
    updated_at: datetime
    messages: Relationship (One-to-Many)
    analytics: Relationship (One-to-Many)

class Message(Base):
    id: str (UUID, Primary Key)
    session_id: str (Foreign Key)
    role: str (Enum: user, assistant, system)
    content: str (Text)
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime
    sequence_number: int

class Challenge(Base):
    id: str (UUID, Primary Key)
    title: str
    description: str (Text)
    difficulty: str (Enum: easy, medium, hard)
    expected_time: int
    category: str
    technology_stack: str
    created_at: datetime
    updated_at: datetime

class Analytics(Base):
    id: str (UUID, Primary Key)
    session_id: str (Foreign Key)
    metric_name: str
    metric_value: float
    timestamp: datetime
    metadata: JSON
```

### 3.3 Data Flow & Request Processing

#### 3.3.1 Chat Message Flow (Detailed)

```
1. User Input (Frontend)
   │
   ├─> Frontend Validation
   │   ├─> Check if session is active
   │   ├─> Check if time remaining > 0
   │   ├─> Estimate tokens for message
   │   └─> Check if tokens available
   │
   ▼
2. Session Service Validation
   │
   ├─> Load session from database
   │   ├─> Verify session status (active/paused)
   │   ├─> Check time remaining
   │   └─> Verify access permissions
   │
   ▼
3. Token Service Pre-flight Check
   │
   ├─> Estimate input tokens (tiktoken)
   ├─> Reserve tokens (atomic operation)
   │   ├─> Check remaining budget
   │   ├─> Reserve estimated tokens
   │   └─> Update session tokens_used
   └─> Return reservation status
   │
   ▼
4. Chat Service Message Processing
   │
   ├─> Format conversation history
   │   ├─> Load previous messages
   │   ├─> Add system prompt
   │   └─> Append user message
   │
   ├─> Apply rate limiting
   │   └─> Check per-session rate limit
   │
   └─> Prepare API request
   │
   ▼
5. OpenAI API Call (Async)
   │
   ├─> Error Handler Wrapper
   │   ├─> Retry on transient errors
   │   ├─> Exponential backoff
   │   └─> Rate limit handling
   │
   ├─> API Request
   │   ├─> POST /v1/chat/completions
   │   ├─> Headers: Authorization, Content-Type
   │   └─> Body: messages, model, temperature, max_tokens
   │
   └─> API Response
       ├─> Extract content
       ├─> Extract usage (input_tokens, output_tokens)
       └─> Handle streaming (if enabled)
   │
   ▼
6. Token Service Post-processing
   │
   ├─> Reconcile token usage
   │   ├─> Actual input tokens from API
   │   ├─> Actual output tokens from API
   │   ├─> Adjust reserved tokens
   │   └─> Update session tokens_used
   │
   └─> Check budget exhaustion
       └─> If budget exhausted, mark session as expired
   │
   ▼
7. Message Persistence
   │
   ├─> Save user message to database
   │   ├─> Message content
   │   ├─> Input tokens
   │   └─> Timestamp
   │
   └─> Save AI response to database
       ├─> Message content
       ├─> Output tokens
       └─> Timestamp
   │
   ▼
8. Session State Update
   │
   ├─> Update session updated_at timestamp
   ├─> Update tokens_used
   └─> Persist to database
   │
   ▼
9. Frontend Update
   │
   ├─> Streamlit rerun triggered
   ├─> Load updated session state
   ├─> Display new messages
   ├─> Update resource panel (timer, tokens)
   └─> Show warnings if needed
```

#### 3.3.2 Timer Flow (Background Worker)

```
Timer Background Worker (Separate Thread)
│
├─> Initialize
│   └─> Load all active sessions
│
└─> Main Loop (Every 1 second)
    │
    ├─> For each active session:
    │   │
    │   ├─> Calculate elapsed time
    │   │   ├─> current_time - start_time
    │   │   └─> Account for paused time
    │   │
    │   ├─> Calculate remaining time
    │   │   └─> time_limit - elapsed_time
    │   │
    │   ├─> Update session state
    │   │   ├─> Update remaining_time (cached)
    │   │   └─> Persist to database (every 10 seconds)
    │   │
    │   ├─> Check expiration
    │   │   ├─> If remaining_time <= 0:
    │   │   │   ├─> Set status = 'expired'
    │   │   │   ├─> Set end_time = now()
    │   │   │   ├─> Disable chat (update session)
    │   │   │   └─> Trigger session end event
    │   │   │
    │   │   └─> Check warning thresholds
    │   │       ├─> 25% remaining: Set warning_level = 'low'
    │   │       ├─> 10% remaining: Set warning_level = 'critical'
    │   │       └─> 5% remaining: Set warning_level = 'urgent'
    │   │
    │   └─> Publish timer event (if using event system)
    │       └─> Notify frontend via state update
    │
    └─> Sleep 1 second
```

#### 3.3.3 Real-time Update Mechanism

**Streamlit State Management**
```python
# Frontend polling mechanism
if st.session_state.get('auto_refresh', True):
    time.sleep(2)  # Poll every 2 seconds
    st.rerun()  # Trigger rerun to update UI

# Session state structure
st.session_state = {
    'session_id': str,
    'session_data': Session,
    'messages': List[Message],
    'last_update': datetime,
    'auto_refresh': bool
}
```

**Backend State Cache (Redis)**
```python
# Cache session state for fast access
redis_cache = {
    f"session:{session_id}:state": {
        "remaining_time": int,
        "tokens_used": int,
        "tokens_remaining": int,
        "status": str,
        "last_updated": timestamp
    },
    "ttl": 3600  # 1 hour
}
```

## 4. Technology Stack

### 4.1 Frontend
- **Streamlit**: Primary UI framework
  - Fast development
  - Built-in state management
  - Easy deployment
  - Real-time updates via reruns

### 4.2 Backend
- **Python 3.9+**: Core language
- **OpenAI Python SDK**: API integration
- **SQLite/PostgreSQL**: Data persistence
  - SQLite for development/single-user
  - PostgreSQL for production/multi-user
- **SQLAlchemy**: ORM for database operations

### 4.3 Additional Libraries
- **streamlit-chat**: Enhanced chat UI components
- **streamlit-option-menu**: Navigation menu
- **pandas**: Data manipulation for analytics
- **plotly**: Interactive charts and graphs
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation
- **asyncio**: Async operations for API calls
- **threading**: Timer management

### 4.4 Deployment
- **Streamlit Cloud**: Easy deployment option
- **Docker**: Containerization for production
- **Environment Variables**: Secure API key management

## 5. Database Schema & Design

### 5.1 Database Technology

**Development**: SQLite
- Lightweight, file-based
- No server setup required
- Suitable for single-user development

**Production**: PostgreSQL
- ACID compliance
- Advanced indexing
- Concurrent access support
- JSON column support for metadata

### 5.2 Core Tables with Indexes

#### Sessions Table
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interviewer_id VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(255) NOT NULL,
    candidate_email VARCHAR(255),
    challenge_id UUID NOT NULL,
    time_limit INTEGER NOT NULL,  -- seconds
    token_budget INTEGER NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    paused_duration INTEGER DEFAULT 0,  -- total paused time in seconds
    status VARCHAR(20) NOT NULL DEFAULT 'created',
        CHECK (status IN ('created', 'active', 'paused', 'completed', 'expired')),
    model_name VARCHAR(50) NOT NULL DEFAULT 'gpt-3.5-turbo',
    system_prompt TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE RESTRICT
);

-- Indexes for performance
CREATE INDEX idx_sessions_interviewer ON sessions(interviewer_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX idx_sessions_challenge ON sessions(challenge_id);

-- Composite index for active session queries
CREATE INDEX idx_sessions_active ON sessions(status, start_time) 
    WHERE status IN ('active', 'paused');
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
        CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    sequence_number INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,  -- Additional metadata (model, finish_reason, etc.)
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_messages_session ON messages(session_id, sequence_number);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_role ON messages(session_id, role);

-- Full-text search index for content
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('english', content));
```

#### Challenges Table
```sql
CREATE TABLE challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
        CHECK (difficulty IN ('easy', 'medium', 'hard')),
    expected_time INTEGER,  -- minutes
    category VARCHAR(100),
    technology_stack VARCHAR(255),
    requirements JSONB,  -- Structured requirements
    sample_solution TEXT,  -- Hidden from candidates
    evaluation_criteria JSONB,
    is_template BOOLEAN DEFAULT false,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_challenges_difficulty ON challenges(difficulty);
CREATE INDEX idx_challenges_category ON challenges(category);
CREATE INDEX idx_challenges_template ON challenges(is_template);
CREATE INDEX idx_challenges_search ON challenges USING gin(to_tsvector('english', title || ' ' || description));
```

#### Analytics Table
```sql
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_type VARCHAR(50),  -- efficiency, usage, quality, etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_analytics_session ON analytics(session_id, timestamp);
CREATE INDEX idx_analytics_metric ON analytics(metric_name, timestamp);
CREATE INDEX idx_analytics_type ON analytics(metric_type);
```

#### Session Events Table (Audit Log)
```sql
CREATE TABLE session_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
        CHECK (event_type IN ('created', 'started', 'paused', 'resumed', 
                             'ended', 'expired', 'time_extended', 
                             'tokens_extended', 'message_sent')),
    event_data JSONB,
    triggered_by VARCHAR(255),  -- user_id or 'system'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_events_session ON session_events(session_id, timestamp);
CREATE INDEX idx_events_type ON session_events(event_type, timestamp);
```

### 5.3 Database Relationships

```
sessions (1) ──< (many) messages
sessions (1) ──< (many) analytics
sessions (1) ──< (many) session_events
challenges (1) ──< (many) sessions
```

### 5.4 Database Optimization Strategies

**Connection Pooling**
```python
# SQLAlchemy connection pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

**Query Optimization**
- Use `select_related` / `joinedload` for eager loading
- Implement pagination for large result sets
- Use database-level aggregation for analytics
- Cache frequently accessed data (challenges, templates)

**Migration Strategy**
- Use Alembic for schema migrations
- Version control all migrations
- Test migrations on staging before production

## 6. API Integration & External Services

### 6.1 OpenAI API Integration

#### 6.1.1 Configuration & Setup

**Environment Variables**
```python
# .env file
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: for custom endpoints
OPENAI_DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30
```

**Client Initialization**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0,
    max_retries=3
)
```

#### 6.1.2 Token Counting Implementation

**Tiktoken Integration**
```python
import tiktoken

class TokenCounter:
    def __init__(self):
        self.encodings = {}  # Cache encodings per model
    
    def get_encoding(self, model: str) -> tiktoken.Encoding:
        """Get or create encoding for model"""
        if model not in self.encodings:
            try:
                self.encodings[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base for unknown models
                self.encodings[model] = tiktoken.get_encoding("cl100k_base")
        return self.encodings[model]
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model"""
        encoding = self.get_encoding(model)
        return len(encoding.encode(text))
    
    def count_message_tokens(self, messages: List[dict], model: str) -> int:
        """Count tokens for chat messages (includes formatting overhead)"""
        encoding = self.get_encoding(model)
        tokens_per_message = 4  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # If there's a name, the role is omitted
        
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        
        num_tokens += 2  # Every reply is primed with <|start|>assistant<|message|>
        return num_tokens
```

**Token Estimation for User Input**
```python
def estimate_user_message_tokens(message: str, model: str) -> int:
    """Estimate tokens for user message before sending"""
    counter = TokenCounter()
    base_tokens = counter.count_tokens(message, model)
    # Add overhead for message formatting
    return base_tokens + 10  # Conservative estimate
```

#### 6.1.3 API Call Implementation

**Async Chat Completion**
```python
async def chat_completion(
    messages: List[dict],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    stream: bool = False
) -> ChatCompletionResponse:
    """Make async API call to OpenAI"""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        return response
    except openai.RateLimitError as e:
        # Handle rate limit
        raise RateLimitException(f"Rate limit exceeded: {e}")
    except openai.APIError as e:
        # Handle API errors
        raise APIException(f"API error: {e}")
```

#### 6.1.4 Error Handling & Retry Logic

**Retry Decorator**
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, TimeoutError, ConnectionError))
)
async def call_openai_with_retry(*args, **kwargs):
    """Wrapper with retry logic"""
    return await client.chat.completions.create(*args, **kwargs)
```

**Error Classification**
```python
class APIErrorHandler:
    def handle_error(self, error: Exception) -> tuple[str, bool]:
        """Return (user_message, should_retry)"""
        if isinstance(error, RateLimitError):
            return ("Rate limit exceeded. Please wait a moment.", True)
        elif isinstance(error, TimeoutError):
            return ("Request timed out. Please try again.", True)
        elif isinstance(error, APIError):
            return ("API error occurred. Please try again.", False)
        else:
            return ("An unexpected error occurred.", False)
```

#### 6.1.5 Cost Calculation

**Model Pricing (as of 2024)**
```python
MODEL_PRICING = {
    "gpt-3.5-turbo": {
        "input": 0.0005 / 1000,   # $0.50 per 1M tokens
        "output": 0.0015 / 1000   # $1.50 per 1M tokens
    },
    "gpt-4": {
        "input": 0.03 / 1000,     # $30 per 1M tokens
        "output": 0.06 / 1000     # $60 per 1M tokens
    },
    "gpt-4-turbo-preview": {
        "input": 0.01 / 1000,     # $10 per 1M tokens
        "output": 0.03 / 1000     # $30 per 1M tokens
    }
}

def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate API cost for tokens used"""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-3.5-turbo"])
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    return input_cost + output_cost
```

### 6.2 Rate Limiting Implementation

#### 6.2.1 Per-Session Rate Limiting

**Redis-Based Rate Limiter**
```python
import redis
from datetime import timedelta

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def check_rate_limit(
        self, 
        session_id: str, 
        limit: int = 60, 
        window: int = 60
    ) -> tuple[bool, int]:
        """
        Check if session is within rate limit
        Returns: (allowed, remaining_requests)
        """
        key = f"rate_limit:session:{session_id}"
        current = self.redis.incr(key)
        
        if current == 1:
            # First request, set expiration
            self.redis.expire(key, window)
        
        if current > limit:
            return False, 0
        
        return True, limit - current
```

#### 6.2.2 Global Rate Limiting

**API-Level Rate Limiting**
```python
class GlobalRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.global_limit = 1000  # requests per minute
        self.window = 60
    
    def check_global_limit(self) -> bool:
        """Check global API rate limit"""
        key = "rate_limit:global"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, self.window)
        
        return current <= self.global_limit
```

### 6.3 Caching Strategy

**Response Caching (Optional)**
```python
class ResponseCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour
    
    def get_cache_key(self, messages: List[dict]) -> str:
        """Generate cache key from messages"""
        import hashlib
        content = json.dumps(messages, sort_keys=True)
        return f"cache:response:{hashlib.md5(content.encode()).hexdigest()}"
    
    def get(self, messages: List[dict]) -> Optional[str]:
        """Get cached response"""
        key = self.get_cache_key(messages)
        return self.redis.get(key)
    
    def set(self, messages: List[dict], response: str):
        """Cache response"""
        key = self.get_cache_key(messages)
        self.redis.setex(key, self.ttl, response)
```

## 7. User Interface Design

### 7.1 Candidate Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  Interview Buddy                    [Timer] [Tokens]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Challenge Panel (Collapsible)                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Challenge: Build a REST API                      │  │
│  │ Description: ...                                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Chat Area                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ User: How do I start?                            │  │
│  │ AI: You can start by...                          │  │
│  │ User: Can you help me with...                    │  │
│  │ AI: ...                                           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  [Message Input Box] [Send Button]                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Interviewer Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Interview Buddy - Dashboard                            │
├─────────────────────────────────────────────────────────┤
│  [Create Session] [View History] [Analytics]            │
│                                                          │
│  Active Sessions                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Session: ABC123 | Candidate: John                │  │
│  │ Time: 25:30 / 30:00 | Tokens: 8,500 / 10,000    │  │
│  │ [View] [Pause] [Extend] [End]                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Session Details (when selected)                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Live Conversation                                │  │
│  │ Token Usage Graph                                │  │
│  │ Performance Metrics                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 8. Security Architecture

### 8.1 API Key Management

**Environment Variable Security**
```python
# Never hardcode API keys
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")

# Validate key format
if not API_KEY.startswith("sk-"):
    raise ValueError("Invalid API key format")
```

**Key Rotation Strategy**
```python
class APIKeyManager:
    def __init__(self):
        self.primary_key = os.getenv("OPENAI_API_KEY")
        self.fallback_key = os.getenv("OPENAI_API_KEY_FALLBACK")
    
    def get_active_key(self) -> str:
        """Get active API key, with fallback"""
        # Could implement health check here
        return self.primary_key or self.fallback_key
    
    def rotate_key(self, new_key: str):
        """Rotate to new API key (admin function)"""
        # Update environment variable
        # Update all active connections
        pass
```

**Frontend Security**
- API keys never sent to frontend
- All API calls made server-side
- Frontend only receives session IDs and display data

### 8.2 Session Security

**Session ID Generation**
```python
import uuid
import secrets

def generate_session_id() -> str:
    """Generate cryptographically secure session ID"""
    # Use UUID4 for uniqueness
    session_uuid = uuid.uuid4()
    # Add random component for extra security
    random_component = secrets.token_urlsafe(8)
    return f"{session_uuid.hex}-{random_component}"
```

**Access Control**
```python
class AccessControl:
    def can_access_session(
        self, 
        session_id: str, 
        user_type: str, 
        user_id: str = None
    ) -> bool:
        """Verify user can access session"""
        session = get_session(session_id)
        
        if user_type == "candidate":
            # Candidates can only access their own session
            # No additional auth required (session ID is secret)
            return True
        
        elif user_type == "interviewer":
            # Interviewers can access sessions they created
            return session.interviewer_id == user_id
        
        elif user_type == "admin":
            # Admins can access all sessions
            return True
        
        return False
```

**Session Expiration**
```python
def check_session_expiry(session_id: str) -> bool:
    """Check if session has expired"""
    session = get_session(session_id)
    
    # Time-based expiration
    if session.status == "expired":
        return True
    
    # Inactivity expiration (e.g., 24 hours)
    if session.updated_at < datetime.now() - timedelta(hours=24):
        expire_session(session_id)
        return True
    
    return False
```

### 8.3 Data Privacy & Encryption

**Encryption at Rest**
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        self.cipher = Fernet(key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive conversation data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive conversation data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

**Data Transmission Security**
- HTTPS/TLS for all communications
- Streamlit Cloud provides HTTPS by default
- Self-hosted: Use reverse proxy (Nginx) with SSL certificates

**GDPR Compliance**
```python
class DataPrivacy:
    def anonymize_session(self, session_id: str):
        """Anonymize session data for GDPR compliance"""
        session = get_session(session_id)
        session.candidate_name = "Anonymous"
        session.candidate_email = None
        # Keep technical data, remove PII
        save_session(session)
    
    def delete_session_data(self, session_id: str):
        """Delete all session data (right to be forgotten)"""
        # Delete messages
        delete_messages(session_id)
        # Delete analytics
        delete_analytics(session_id)
        # Delete session
        delete_session(session_id)
    
    def export_user_data(self, candidate_email: str) -> dict:
        """Export all user data (data portability)"""
        sessions = get_sessions_by_email(candidate_email)
        return {
            "sessions": [serialize_session(s) for s in sessions],
            "messages": [serialize_messages(s.id) for s in sessions]
        }
```

**Data Retention Policy**
```python
def cleanup_old_sessions():
    """Automated cleanup of old sessions"""
    cutoff_date = datetime.now() - timedelta(days=90)  # 90-day retention
    
    old_sessions = db.query(Session).filter(
        Session.created_at < cutoff_date,
        Session.status.in_(['completed', 'expired'])
    ).all()
    
    for session in old_sessions:
        anonymize_session(session.id)
        # Or delete if beyond retention period
```

### 8.4 Input Sanitization & Validation

**Input Validation**
```python
import re
from html import escape

class InputSanitizer:
    MAX_MESSAGE_LENGTH = 10000
    MAX_SESSION_NAME_LENGTH = 255
    
    def sanitize_message(self, message: str) -> str:
        """Sanitize user message input"""
        # Remove null bytes
        message = message.replace('\x00', '')
        
        # Trim whitespace
        message = message.strip()
        
        # Check length
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message too long (max {self.MAX_MESSAGE_LENGTH} chars)")
        
        # Escape HTML (if displaying in UI)
        # message = escape(message)  # Only if needed
        
        return message
    
    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format"""
        pattern = r'^[a-f0-9]{32}-[A-Za-z0-9_-]{11}$'
        return bool(re.match(pattern, session_id))
```

**Prompt Injection Prevention**
```python
class PromptInjectionDetector:
    SUSPICIOUS_PATTERNS = [
        r'ignore\s+(previous|above|earlier)',
        r'forget\s+(everything|all)',
        r'you\s+are\s+now',
        r'system\s*:',
        r'<\|.*?\|>',  # Special tokens
    ]
    
    def detect_injection(self, message: str) -> bool:
        """Detect potential prompt injection attempts"""
        message_lower = message.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        return False
    
    def sanitize_for_api(self, message: str) -> str:
        """Sanitize message before sending to API"""
        if self.detect_injection(message):
            # Log suspicious activity
            log_security_event("prompt_injection_attempt", message)
            # Could block or sanitize further
            return self.escape_special_tokens(message)
        return message
```

**Content Filtering (Optional)**
```python
class ContentFilter:
    def __init__(self):
        self.blocked_patterns = [
            # Add patterns for inappropriate content
        ]
    
    def filter_content(self, content: str) -> tuple[str, bool]:
        """
        Filter content
        Returns: (filtered_content, is_blocked)
        """
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return content, True
        return content, False
```

### 8.5 Authentication & Authorization

**Session-Based Auth (Future Enhancement)**
```python
# For multi-user scenarios
class AuthManager:
    def create_user_session(self, user_id: str, role: str) -> str:
        """Create authenticated user session"""
        session_token = secrets.token_urlsafe(32)
        # Store in Redis with expiration
        redis.setex(
            f"auth:session:{session_token}",
            3600,  # 1 hour
            json.dumps({"user_id": user_id, "role": role})
        )
        return session_token
    
    def verify_session(self, session_token: str) -> dict:
        """Verify and get user info from session token"""
        data = redis.get(f"auth:session:{session_token}")
        if data:
            return json.loads(data)
        return None
```

## 9. Performance Optimization & Scalability

### 9.1 Frontend Optimization

**Streamlit Rerun Optimization**
```python
# Minimize reruns
import time

class RerunController:
    def __init__(self):
        self.last_rerun = time.time()
        self.rerun_interval = 2  # seconds
    
    def should_rerun(self) -> bool:
        """Control when to trigger rerun"""
        now = time.time()
        if now - self.last_rerun >= self.rerun_interval:
            self.last_rerun = now
            return True
        return False

# Use in main loop
if rerun_controller.should_rerun():
    st.rerun()
```

**State Management Optimization**
```python
# Cache expensive computations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_challenge_data(challenge_id: str):
    """Cache challenge data"""
    return challenge_service.get_challenge(challenge_id)

# Use session state efficiently
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.last_message_id = None
```

**Lazy Loading**
```python
# Load messages in batches
def load_messages(session_id: str, limit: int = 50, offset: int = 0):
    """Load messages with pagination"""
    return db.query(Message)\
        .filter(Message.session_id == session_id)\
        .order_by(Message.timestamp.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
```

### 9.2 Backend Optimization

**Database Connection Pooling**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Disable SQL logging in production
)
```

**Query Optimization**
```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

session = db.query(Session)\
    .options(joinedload(Session.messages))\
    .filter(Session.id == session_id)\
    .first()

# Use select_related for foreign keys
messages = db.query(Message)\
    .join(Session)\
    .filter(Session.id == session_id)\
    .all()
```

**Caching Strategy**
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
def get_challenge_templates():
    """Cached challenge templates"""
    return challenge_service.list_templates()
```

**Async Operations**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

async def process_chat_message(session_id: str, message: str):
    """Async message processing"""
    # Run blocking operations in thread pool
    loop = asyncio.get_event_loop()
    session = await loop.run_in_executor(
        executor,
        session_service.get_session,
        session_id
    )
    
    # Async API call
    response = await openai_client.chat_completion(...)
    
    return response
```

### 9.3 Scalability Considerations

**Horizontal Scaling Architecture**
```
                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   Streamlit App 1  Streamlit App 2  Streamlit App 3
        │                │                │
        └────────────────┼────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
        PostgreSQL (Primary)   Redis Cluster
              │                     │
        PostgreSQL (Replica)   Redis (Replica)
```

**Database Scaling**
- Read replicas for analytics queries
- Partitioning for large tables (by date)
- Connection pooling per application instance
- Query result caching

**Session State Management (Multi-Instance)**
```python
# Use Redis for shared session state
class DistributedSessionState:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_session_state(self, session_id: str) -> dict:
        """Get session state from Redis"""
        data = self.redis.get(f"session:state:{session_id}")
        return json.loads(data) if data else {}
    
    def update_session_state(self, session_id: str, state: dict):
        """Update session state in Redis"""
        self.redis.setex(
            f"session:state:{session_id}",
            3600,  # 1 hour TTL
            json.dumps(state)
        )
```

**Background Job Processing**
```python
# Use Celery for background tasks (optional)
from celery import Celery

celery_app = Celery('interview_buddy')

@celery_app.task
def cleanup_expired_sessions():
    """Background task to cleanup expired sessions"""
    expired = session_service.get_expired_sessions()
    for session in expired:
        session_service.end_session(session.id)

@celery_app.task
def calculate_analytics(session_id: str):
    """Background task for analytics calculation"""
    analytics_service.generate_report(session_id)
```

**Resource Monitoring**
```python
import psutil
import logging

class ResourceMonitor:
    def check_resources(self):
        """Monitor system resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if cpu_percent > 80:
            logging.warning(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > 80:
            logging.warning(f"High memory usage: {memory.percent}%")
        
        return {
            "cpu": cpu_percent,
            "memory": memory.percent,
            "available": memory.available
        }
```

## 10. Testing Strategy

### 10.1 Unit Tests
- Token counting accuracy
- Timer functionality
- Session state management
- API integration mocks

### 10.2 Integration Tests
- End-to-end chat flow
- Limit enforcement
- Session lifecycle
- Error handling

### 10.3 User Acceptance Testing
- Candidate experience
- Interviewer workflow
- Edge cases (rapid messages, network failures)

## 11. Deployment Plan

### 11.1 Development Environment
- Local Streamlit app
- SQLite database
- Environment variables for API keys

### 11.2 Production Deployment
- Streamlit Cloud or custom server
- PostgreSQL database
- Environment variable management
- SSL/TLS encryption
- Monitoring and logging

### 11.3 Docker Deployment

**Dockerfile**
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

**Docker Compose**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/interview_buddy
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=interview_buddy
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**Production Deployment Checklist**
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL/TLS certificates installed
- [ ] Reverse proxy (Nginx) configured
- [ ] Monitoring and logging setup
- [ ] Backup strategy implemented
- [ ] Security hardening applied
- [ ] Performance testing completed

## 12. Future Enhancements

### 12.1 Phase 2 Features
- Multi-language support
- Voice input/output
- Screen sharing integration
- Collaborative sessions (multiple candidates)

### 12.2 Advanced Analytics
- AI-powered candidate assessment
- Skill gap analysis
- Performance benchmarking
- Comparative analytics

### 12.3 Integration Capabilities
- HR system integration
- Calendar integration
- Email notifications
- Report generation

### 12.4 Enhanced AI Features
- Multiple AI model support (Claude, Gemini)
- Custom fine-tuned models
- Context-aware suggestions
- Code execution environment

## 13. Project Structure

```
interview-buddy/
├── app.py                      # Main Streamlit application
├── pages/
│   ├── candidate.py           # Candidate interface
│   ├── interviewer.py          # Interviewer dashboard
│   └── admin.py                # Admin panel
├── services/
│   ├── session_service.py
│   ├── token_service.py
│   ├── timer_service.py
│   ├── chat_service.py
│   ├── challenge_service.py
│   └── analytics_service.py
├── api/
│   ├── openai_client.py
│   ├── rate_limiter.py
│   └── error_handler.py
├── models/
│   ├── models.py
│   └── database.py
├── components/
│   ├── resource_panel.py
│   ├── chat_interface.py
│   ├── challenge_display.py
│   └── analytics_view.py
├── utils/
│   ├── token_counter.py
│   ├── validators.py
│   └── helpers.py
├── config/
│   ├── settings.py
│   └── constants.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── data/
│   └── challenges/             # Challenge templates
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```

## 14. Implementation Phases

### Phase 1: MVP (Week 1-2)
- Basic chat interface
- Timer functionality
- Token tracking
- Simple session management
- OpenAI integration

### Phase 2: Core Features (Week 3-4)
- Interviewer dashboard
- Session configuration
- Challenge management
- Enhanced UI/UX
- Error handling

### Phase 3: Advanced Features (Week 5-6)
- Analytics and insights
- Session history
- Export functionality
- Performance optimizations
- Testing and bug fixes

### Phase 4: Polish & Deploy (Week 7-8)
- UI/UX refinements
- Documentation
- Deployment setup
- Security hardening
- User acceptance testing

## 15. Success Metrics

### 15.1 Technical Metrics
- API response time < 3 seconds
- Token counting accuracy > 99%
- Timer accuracy ±1 second
- System uptime > 99%

### 15.2 User Experience Metrics
- Session completion rate
- Average token efficiency
- User satisfaction scores
- Error rate < 1%

### 15.3 Business Metrics
- Number of interviews conducted
- Average session duration
- Token budget utilization
- Interviewer adoption rate

## 16. Risk Assessment

### 16.1 Technical Risks
- **API Rate Limits**: Mitigated by rate limiting and queuing
- **Token Counting Inaccuracy**: Use official tiktoken library
- **Timer Drift**: Use server-side time tracking
- **State Management**: Robust session persistence

### 16.2 Business Risks
- **API Cost Overruns**: Strict token budget enforcement
- **User Adoption**: Intuitive UI and clear documentation
- **Scalability**: Design for horizontal scaling

## 17. API Specifications

### 17.1 Internal Service APIs

**Session Service API**
```python
# services/session_service.py

class SessionService:
    def create_session(config: SessionConfig) -> Session:
        """
        Create new interview session
        Returns: Session object with generated ID
        """
        pass
    
    def get_session(session_id: str) -> Optional[Session]:
        """
        Retrieve session by ID
        Returns: Session object or None if not found
        """
        pass
    
    def update_session(session_id: str, **updates) -> Session:
        """
        Update session attributes
        Returns: Updated session
        """
        pass
    
    def pause_session(session_id: str) -> Session:
        """Pause active session"""
        pass
    
    def resume_session(session_id: str) -> Session:
        """Resume paused session"""
        pass
    
    def end_session(session_id: str) -> Session:
        """Manually end session"""
        pass
```

**Token Service API**
```python
# services/token_service.py

class TokenService:
    def estimate_tokens(text: str, model: str) -> int:
        """Estimate token count for text"""
        pass
    
    def reserve_tokens(session_id: str, estimated: int) -> bool:
        """
        Reserve tokens before API call
        Returns: True if reservation successful
        """
        pass
    
    def update_consumption(
        self, 
        session_id: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> TokenUsage:
        """Update actual token consumption after API call"""
        pass
    
    def get_remaining_budget(session_id: str) -> int:
        """Get remaining token budget"""
        pass
    
    def check_budget(session_id: str, estimated: int) -> bool:
        """Check if budget allows for estimated tokens"""
        pass
```

### 17.2 Data Transfer Objects (DTOs)

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionConfig(BaseModel):
    interviewer_id: str
    candidate_name: str
    candidate_email: Optional[str]
    challenge_id: str
    time_limit: int  # seconds
    token_budget: int
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    system_prompt: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    status: str
    time_remaining: int
    tokens_used: int
    tokens_remaining: int
    created_at: datetime
    updated_at: datetime

class MessageRequest(BaseModel):
    content: str
    session_id: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime

class TokenUsage(BaseModel):
    session_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: datetime
```

## 18. Error Handling & Logging

### 18.1 Error Types

```python
class InterviewBuddyException(Exception):
    """Base exception"""
    pass

class SessionNotFoundError(InterviewBuddyException):
    """Session not found"""
    pass

class SessionExpiredError(InterviewBuddyException):
    """Session has expired"""
    pass

class TokenBudgetExceededError(InterviewBuddyException):
    """Token budget exceeded"""
    pass

class RateLimitExceededError(InterviewBuddyException):
    """Rate limit exceeded"""
    pass

class APIError(InterviewBuddyException):
    """OpenAI API error"""
    pass
```

### 18.2 Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/interview_buddy.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.INFO)
```

### 18.3 Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    code: str
    details: Optional[dict] = None
    timestamp: datetime = datetime.now()

# Example usage
def handle_error(error: Exception) -> ErrorResponse:
    if isinstance(error, SessionNotFoundError):
        return ErrorResponse(
            error="SessionNotFound",
            message="The requested session was not found",
            code="SESSION_404"
        )
    # ... other error types
```

## 19. Monitoring & Observability

### 19.1 Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
session_created = Counter('sessions_created_total', 'Total sessions created')
session_completed = Counter('sessions_completed_total', 'Total sessions completed')
api_calls_total = Counter('api_calls_total', 'Total API calls', ['model'])
api_call_duration = Histogram('api_call_duration_seconds', 'API call duration')
active_sessions = Gauge('active_sessions', 'Number of active sessions')
tokens_consumed = Counter('tokens_consumed_total', 'Total tokens consumed', ['type'])

# Usage
session_created.inc()
api_call_duration.observe(duration)
active_sessions.set(count)
```

### 19.2 Health Checks

```python
def health_check() -> dict:
    """System health check endpoint"""
    checks = {
        "database": check_database_connection(),
        "redis": check_redis_connection(),
        "openai": check_openai_connection(),
        "disk_space": check_disk_space()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

## 20. Testing Architecture

### 20.1 Unit Testing Structure

```python
# tests/unit/test_token_service.py
import pytest
from services.token_service import TokenService

class TestTokenService:
    def test_estimate_tokens(self):
        service = TokenService()
        tokens = service.estimate_tokens("Hello world", "gpt-3.5-turbo")
        assert tokens > 0
    
    def test_reserve_tokens(self):
        service = TokenService()
        session_id = "test-session"
        # Setup session
        result = service.reserve_tokens(session_id, 100)
        assert result is True
```

### 20.2 Integration Testing

```python
# tests/integration/test_chat_flow.py
@pytest.mark.asyncio
async def test_complete_chat_flow():
    """Test complete chat message flow"""
    # Create session
    session = await session_service.create_session(config)
    
    # Send message
    response = await chat_service.send_message(
        session.id, 
        "Hello, can you help me?"
    )
    
    assert response.role == "assistant"
    assert response.content is not None
    assert response.total_tokens > 0
```

### 20.3 Mock Services

```python
# tests/fixtures/mocks.py
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('api.openai_client.AsyncOpenAI') as mock:
        mock.return_value.chat.completions.create = AsyncMock(
            return_value=MockResponse(
                choices=[MockChoice(message=MockMessage(content="Test response"))],
                usage=MockUsage(prompt_tokens=10, completion_tokens=20)
            )
        )
        yield mock
```

## 21. Conclusion

Interview Buddy provides a comprehensive, production-ready solution for evaluating candidates' AI-assisted problem-solving abilities. The architecture is designed to be:

- **Scalable**: Horizontal scaling support, efficient database queries, caching strategies
- **Maintainable**: Modular service architecture, clear separation of concerns, comprehensive testing
- **Secure**: Input validation, encryption, access control, audit logging
- **Performant**: Async operations, connection pooling, optimized queries, caching
- **Observable**: Logging, metrics, health checks, error tracking

The technical architecture leverages Python and Streamlit for rapid development while maintaining enterprise-grade quality through proper design patterns, security measures, and scalability considerations. The modular design allows for future enhancements and integrations without major refactoring.

Key technical achievements:
- Precise token counting using tiktoken
- Server-side timer enforcement preventing client manipulation
- Real-time state synchronization across multiple instances
- Comprehensive error handling and retry logic
- Production-ready deployment configurations

The system addresses a real need in modern technical interviews where AI tools are becoming standard, and the ability to use them efficiently is a valuable skill. By providing clear constraints, real-time feedback, and comprehensive analytics, Interview Buddy creates a fair, standardized, and insightful assessment environment.

