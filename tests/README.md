# Testing the Weather Sensor API

This directory contains tests for the Weather Sensor API.

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/models/test_models.py
```

To run a specific test:

```bash
pytest tests//models/test_models.py::test_sensor_model
```

## Coverage

To get test coverage, install pytest-cov:

```bash
pip install pytest-cov
```

Then run:

```bash
pytest --cov=src
```

For a detailed HTML coverage report:

```bash
pytest --cov=src --cov-report=html
```

## Test Structure

The tests are organized to mirror the project structure:

- `conftest.py`: Test fixtures shared across test files
- `test_database.py`: Tests for database connectivity
- `test_models.py`: Tests for SQLAlchemy models
- `test_schemas.py`: Tests for Pydantic validation schemas
- `test_sensors.py`: Tests for sensor endpoints
- `test_metrics.py`: Tests for metrics endpoints
- `test_queries.py`: Tests for query endpoints
- `test_helpers.py`: Tests for utility functions
- `test_test_endpoints.py`: Tests for the test data creation endpoints