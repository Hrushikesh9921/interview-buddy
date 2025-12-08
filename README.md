# 🎯 Interview Buddy

AI-powered interview practice platform with comprehensive resource tracking and real-time monitoring.

## Overview

Interview Buddy is a sophisticated platform that enables candidates to practice technical interviews with AI assistance while providing interviewers with powerful monitoring and analytics tools. Built with Streamlit and OpenAI's GPT models, it tracks token usage, time limits, and provides detailed performance analytics.

## Features

### For Candidates
- 💬 **AI-Powered Chat Interface** - Practice interviews with intelligent AI assistance
- ⏱️ **Time Tracking** - Countdown timer with visual warnings
- 🎯 **Token Budget Management** - Real-time token usage tracking
- 📝 **Challenge Library** - Pre-built coding challenges and custom problems
- 📊 **Performance Insights** - Review your efficiency and resource usage

### For Interviewers
- 👀 **Real-Time Monitoring** - Watch candidate progress live
- 🎛️ **Session Controls** - Pause, extend, and manage sessions
- 📈 **Analytics Dashboard** - Detailed performance metrics
- 📜 **Session History** - Review and export past sessions
- 📤 **Export Functionality** - Export conversations in multiple formats

## Tech Stack

- **Framework**: Python 3.9+, Streamlit
- **AI Integration**: OpenAI API (GPT-4)
- **Database**: SQLite (development), PostgreSQL (production)
- **Token Counting**: tiktoken
- **Analytics**: Plotly, Pandas

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   cd interview-buddy
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_api_key_here
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Open your browser**
   - Navigate to `http://localhost:8501`

## Project Structure

```
interview-buddy/
├── app.py                      # Main application entry point
├── pages/                      # Page components
│   ├── candidate.py           # Candidate interface
│   └── interviewer.py         # Interviewer dashboard
├── services/                   # Business logic services
│   ├── session_service.py     # Session management
│   ├── chat_service.py        # Chat functionality
│   ├── token_service.py       # Token tracking
│   └── analytics_service.py   # Analytics calculations
├── api/                        # External API integrations
│   └── openai_client.py       # OpenAI API client
├── models/                     # Database models
│   ├── database.py            # Database setup
│   └── models.py              # SQLAlchemy models
├── components/                 # Reusable UI components
│   ├── shared/                # Shared components
│   ├── candidate/             # Candidate-specific components
│   └── interviewer/           # Interviewer-specific components
├── utils/                      # Utility functions
│   ├── logger.py              # Logging configuration
│   └── token_counter.py       # Token counting utilities
├── config/                     # Configuration
│   ├── settings.py            # Application settings
│   └── constants.py           # Application constants
├── tests/                      # Test suite
├── data/                       # Database and data files
├── scripts/                    # Utility scripts
│   └── init_db.py             # Database initialization
├── requirements.txt            # Python dependencies
├── env.example                # Example environment file
└── README.md                  # This file
```

## Configuration

All configuration is managed through environment variables. See `env.example` for all available options.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | gpt-4 |
| `DEFAULT_SESSION_DURATION` | Default time limit (seconds) | 3600 |
| `DEFAULT_TOKEN_BUDGET` | Default token budget | 50000 |
| `DATABASE_URL` | Database connection string | sqlite:///./data/interview_buddy.db |

## Usage

### Creating a Session

1. Navigate to "Create Session" in the sidebar
2. Enter candidate information
3. Set time limit and token budget
4. Select or enter a challenge
5. Share the generated session ID with the candidate

### Candidate Workflow

1. Navigate to "Candidate Interface"
2. Enter your session ID
3. Start chatting with the AI
4. Monitor your time and token usage
5. Complete the challenge within the limits

### Interviewer Workflow

1. Navigate to "Interviewer Dashboard"
2. Select an active session to monitor
3. Watch the conversation in real-time
4. Use controls to pause, extend, or end the session
5. Review analytics after completion

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_token_service.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Development Roadmap

- [x] **Phase 0**: Project foundation and setup ✅
- [ ] **Phase 1**: Token service and OpenAI integration
- [ ] **Phase 2**: Session management
- [ ] **Phase 3**: Chat interface (MVP)
- [ ] **Phase 4**: Timer system
- [ ] **Phase 5**: Interviewer dashboard
- [ ] **Phase 6**: Challenge management
- [ ] **Phase 7**: Enhanced controls
- [ ] **Phase 8**: Analytics
- [ ] **Phase 9**: History and export
- [ ] **Phase 10**: UI polish
- [ ] **Phase 11**: Security
- [ ] **Phase 12**: Performance optimization
- [ ] **Phase 13**: Testing
- [ ] **Phase 14**: Documentation
- [ ] **Phase 15**: Production deployment

See `execution_plan.md` for detailed phase breakdown.

## Architecture

For detailed architecture documentation, see `ARCHITECTURE.md`.

## Contributing

This is currently a private project. For questions or contributions, please contact the project maintainer.

## License

Copyright © 2025. All rights reserved.

## Support

For issues, questions, or feature requests, please refer to the project documentation or contact the development team.

---

**Built with ❤️ using Streamlit and OpenAI**

