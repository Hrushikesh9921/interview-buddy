"""
Tests for logging utility.
"""
import pytest
import logging
from utils.logger import setup_logger


class TestLogger:
    """Test logger configuration."""
    
    def test_logger_setup(self):
        """Test logger setup."""
        logger = setup_logger("test_logger")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_logger_level(self):
        """Test logger level configuration."""
        logger = setup_logger("test_logger_level")
        
        # Default should be INFO or from settings
        assert logger.level in [logging.INFO, logging.DEBUG]
    
    def test_logger_has_handlers(self):
        """Test logger has handlers."""
        logger = setup_logger("test_logger_handlers")
        
        assert len(logger.handlers) > 0
    
    def test_logger_logging(self, caplog):
        """Test actual logging."""
        logger = setup_logger("test_logger_log")
        
        with caplog.at_level(logging.INFO):
            logger.info("Test info message")
            logger.warning("Test warning message")
        
        assert "Test info message" in caplog.text
        assert "Test warning message" in caplog.text

