"""
Pytest configuration and fixtures.
"""
import os
import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base
from config.settings import Settings


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["DEBUG"] = "True"
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield
    # Cleanup
    for key in ["OPENAI_API_KEY", "DATABASE_URL", "DEBUG", "LOG_LEVEL"]:
        os.environ.pop(key, None)


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create session
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_settings(test_env):
    """Create test settings instance."""
    return Settings(
        openai_api_key="sk-test-key",
        openai_model="gpt-4",
        database_url="sqlite:///:memory:",
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

