from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from src.database.init_db import init_database


@patch('src.database.init_db.Base')
@patch('src.database.init_db.engine')
@patch('src.database.init_db.logger')
def test_init_database_success(mock_logger, mock_engine, mock_base):
    """Test successful database initialization."""
    # Setup the mock
    mock_base.metadata.create_all = MagicMock()

    # Call the function
    result = init_database()

    # Verify the result
    assert result is True

    # Verify the mocks were called correctly
    mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_called_with("Database tables created successfully.")


@patch('src.database.init_db.Base')
@patch('src.database.init_db.engine')
@patch('src.database.init_db.logger')
def test_init_database_failure(mock_logger, mock_engine, mock_base):
    """Test database initialization failure."""
    # Setup the mock to raise a SQLAlchemyError
    mock_base.metadata.create_all = MagicMock(side_effect=SQLAlchemyError("Database error"))

    # Call the function
    result = init_database()

    # Verify the result
    assert result is False

    # Verify the error was logged
    mock_logger.error.assert_called()