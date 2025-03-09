"""
Database initialization script that can be run independently to ensure
the database and tables are properly created before starting the API.
"""
import os
import sys

# Add the parent directory to sys.path to allow importing from src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from sqlalchemy.exc import SQLAlchemyError
from src.database.database import Base, engine
from src.utils.logging_config import logger

def init_database():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Starting database initialization...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("Database initialized successfully.")
        sys.exit(0)
    else:
        print("Database initialization failed. Check the logs for details.")
        sys.exit(1)