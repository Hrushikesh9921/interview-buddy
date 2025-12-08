# Interview Buddy - Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create Conda Environment

```bash
conda create -n buddy python=3.11 -y
conda activate buddy
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Create .env file from template
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Initialize Database

```bash
python scripts/init_db.py
```

### Step 5: Verify Setup

```bash
python scripts/verify_setup.py
```

### Step 6: Run Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Detailed Configuration

### Environment Variables

Edit the `.env` file to customize:

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional (defaults shown)
OPENAI_MODEL=gpt-4
DEFAULT_SESSION_DURATION=3600    # 1 hour
DEFAULT_TOKEN_BUDGET=50000
```

### Database Configuration

**Development (default):**
```bash
DATABASE_URL=sqlite:///./data/interview_buddy.db
```

**Production (PostgreSQL):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/interview_buddy
```

---

## Troubleshooting

### Issue: "OpenAI API key not set"

**Solution:** Add your API key to `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

Get an API key at: https://platform.openai.com/api-keys

### Issue: "Module not found"

**Solution:** Ensure conda environment is activated and dependencies are installed:
```bash
conda activate buddy
pip install -r requirements.txt
```

### Issue: "Database error"

**Solution:** Reinitialize the database:
```bash
python scripts/init_db.py
```

### Issue: "Port 8501 already in use"

**Solution:** Either:
1. Stop the existing Streamlit process
2. Run on a different port: `streamlit run app.py --server.port 8502`

---

## Development Workflow

### Activate Environment

Always activate the conda environment before working:
```bash
conda activate buddy
```

### Run the App

```bash
streamlit run app.py
```

### Run Tests

```bash
pytest
```

### Check Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

---

## Project Status

✅ **Phase 0 Complete** - Project Foundation & Setup
- Directory structure created
- Configuration system implemented
- Database models defined
- Basic Streamlit app with navigation
- Development environment ready

**Next Phase:** Phase 1 - Token Service & OpenAI Integration

---

## Getting Help

- **Documentation:** See README.md and ARCHITECTURE.md
- **Execution Plan:** See execution_plan.md for development roadmap
- **Issues:** Check the troubleshooting section above

---

**Happy Coding! 🚀**

