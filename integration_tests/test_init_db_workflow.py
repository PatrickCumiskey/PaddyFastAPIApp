import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from src.database.database import Base
from src.models.models import Sensor


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = db_file.name
    db_file.close()

    yield db_path

    # Clean up after the test
    try:
        if os.path.exists(db_path):
            os.unlink(db_path)
    except Exception as e:
        print(f"Warning: Could not delete test database: {e}")


def test_db_initialization(temp_db_path):
    """Test actual database table creation."""
    # Create a test engine with the temporary db
    test_url = f"sqlite:///{temp_db_path}"
    engine = create_engine(test_url)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Check if the tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Verify expected tables exist
    assert "sensors" in tables
    assert "metrics" in tables

    # Create a session and test basic operations
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    # Create a test sensor
    test_sensor = Sensor(name="Test", location="Test Location")
    session.add(test_sensor)
    session.commit()

    # Query the sensor
    db_sensor = session.query(Sensor).first()
    assert db_sensor is not None
    assert db_sensor.name == "Test"

    # Clean up
    session.close()