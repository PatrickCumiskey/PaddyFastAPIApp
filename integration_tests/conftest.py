"""
Configuration and fixtures for integration tests.
Integration tests use a real test database (test.db) and
test the entire API from HTTP requests to database storage.
"""
import os
import tempfile
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.database import Base, get_db
# Import your app and models
from src.main import app


# Create a temporary database file
@pytest.fixture(scope="session")
def temp_db_path():
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = db_file.name
    db_file.close()

    yield db_path

    # Clean up the temp file after tests
    # On Windows, we might need to retry deletion if the file is still in use
    max_retries = 5
    for i in range(max_retries):
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
            break
        except PermissionError:
            if i < max_retries - 1:
                # Wait briefly for any open handles to be released
                time.sleep(0.5)
            else:
                print(f"Warning: Could not delete temporary database file: {db_path}")


# Setup the database
@pytest.fixture(scope="session")
def test_engine(temp_db_path):
    # Create a test database URL
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db_path}"

    # Create an engine that connects to the test database
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Dispose of the engine to close all connections
    engine.dispose()

# Create a test session factory
@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Setup the TestClient with the test database
@pytest.fixture(scope="function")
def client(test_engine, test_session_factory):
    # Create a test session
    TestingSessionLocal = test_session_factory

    # Override the dependency in the app
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a TestClient
    with TestClient(app) as test_client:
        yield test_client

    # Reset the database after each test - use try/except to avoid errors
    try:
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
    except Exception as e:
        print(f"Warning: Error resetting test database: {e}")

    # Reset the dependency override
    app.dependency_overrides = {}

# Create a DB session for test setup
@pytest.fixture(scope="function")
def db_session(test_session_factory):
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()