# Integration Tests for Weather Sensor API

This directory contains integration tests for the Weather Sensor API. Unlike unit tests, these tests verify how multiple components of the system work together by making actual HTTP requests to the API and interacting with a test database.

## Purpose of integration tests

- **Full API Flow**: Tests the complete request-response cycle
- **Real Database**: Uses a real SQLite database file (temporary)
- **No Mocks**: Uses actual components rather than mocks
- **End-to-End Testing**: Verifies entire workflows rather than isolated functions

## Setup

The integration tests use a separate test database and the FastAPI TestClient to make requests to the API without starting a server.

## Running the Tests

To run all integration tests:

```bash
pytest integration_tests/
```

To run a specific test file:

```bash
pytest integration_tests/test_sensor_workflow.py
```

To run a specific test function:

```bash
pytest integration_tests/test_sensor_workflow.py::test_create_and_get_sensor
```

## Test Organization

- **test_sensor_workflow.py**: Tests for creating and retrieving sensors
- **test_metric_workflow.py**: Tests for recording and retrieving metrics
- **test_query_workflow.py**: Tests for querying metrics with various parameters
- **test_error_handling.py**: Tests for error handling scenarios