"""
Unit tests for the logging_config module.
"""
import logging
from pathlib import Path

import pytest

# Import the logging_config module after setup
from src.utils import logging_config


def test_logger_setup():
    """Test that the logger is correctly set up."""
    # Get the logger
    logger = logging_config.logger

    # Verify it's a logging.Logger instance
    assert isinstance(logger, logging.Logger)

    # Verify logger name matches our app
    assert logger.name == "weather_api"

    # Verify logger level
    assert logger.level == logging.INFO


def test_logger_handlers():
    """Test that the logger has the correct handlers."""
    # Get the logger
    logger = logging_config.logger

    # Should have at least 2 handlers (console and file)
    assert len(logger.handlers) >= 2

    # Verify handler types
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.handlers.RotatingFileHandler in handler_types

    # Verify file handler configuration
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) > 0

    file_handler = file_handlers[0]
    assert file_handler.maxBytes == 10485760  # 10MB
    assert file_handler.backupCount == 5


def test_logs_directory_creation():
    """Test that the logs directory is created."""
    # The logs directory should exist
    logs_dir = Path("logs")
    assert logs_dir.exists()
    assert logs_dir.is_dir()


@pytest.mark.parametrize("level", [
    "debug", "info", "warning", "error", "critical"
])
def test_logger_levels(level, caplog):
    """Test that the logger correctly logs at different levels."""
    # Set caplog to capture INFO and above
    caplog.set_level(logging.INFO)

    # Get the logger
    logger = logging_config.logger

    # Log a message at the specified level
    message = f"Test {level} message"
    getattr(logger, level)(message)

    # For INFO and above, message should be in the log
    if level != "debug":  # debug is below our set level
        assert message in caplog.text
    else:
        # debug messages shouldn't be in the log because we set level to INFO
        assert message not in caplog.text


def test_log_formatting():
    """Test that log messages are correctly formatted."""
    # This is more of an integration test, but we'll check basic formatting
    # by examining the formatters on the handlers

    # Get the logger
    logger = logging_config.logger

    # Check console handler formatter
    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)
                        and not isinstance(h, logging.FileHandler)]
    assert len(console_handlers) > 0

    console_formatter = console_handlers[0].formatter
    assert "%(levelname)s" in console_formatter._fmt
    assert "%(message)s" in console_formatter._fmt

    # Check file handler formatter
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) > 0

    file_formatter = file_handlers[0].formatter
    assert "%(asctime)s" in file_formatter._fmt
    assert "%(name)s" in file_formatter._fmt
    assert "%(levelname)s" in file_formatter._fmt
    assert "%(message)s" in file_formatter._fmt