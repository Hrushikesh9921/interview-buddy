#!/usr/bin/env python
"""
Database initialization script.
Run this script to create all database tables.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import init_db
from utils.logger import logger
from config.settings import settings


def main():
    """Initialize the database."""
    try:
        logger.info(f"Initializing database at: {settings.database_url}")
        
        # Create data directory if it doesn't exist
        if settings.database_path:
            settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        init_db()
        
        logger.info("Database initialization complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

