from sqlalchemy import text


def test_db_connection(test_db):
    """Test that the database connection works"""
    # If this test runs, it means the fixture worked
    assert test_db is not None

    # Test basic query functionality
    result = test_db.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_db_session(test_db):
    """Test that the database session can execute transactions"""
    # Start a transaction
    test_db.begin()

    # Execute a simple query
    test_db.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY)"))
    test_db.execute(text("INSERT INTO test VALUES (1)"))
    result = test_db.execute(text("SELECT id FROM test")).scalar()

    assert result == 1

    # Rollback the transaction
    test_db.rollback()