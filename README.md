# Weather Sensor API

A RESTful API for collecting and querying weather sensor data.

## Features

- Register sensors
- Record metric values (temperature, humidity, wind speed, etc.)
- Query sensor data with various filters:
  - Select specific sensors
  - Choose metrics to analyze
  - Apply statistical functions (min, max, sum, avg)
  - Specify date ranges

## Technical Stack

- Python 3.8+
- FastAPI for API framework
- SQLAlchemy for ORM
- SQLite for database (can be replaced with other DB engines)
- Pydantic for data validation

## Project Structure

```
src/
  ├── __init__.py
  ├── main.py                # FastAPI application initialization
  ├── models/
  │   ├── __init__.py
  │   └── models.py          # SQLAlchemy models
  ├── database/
  │   ├── __init__.py
  │   └── database.py        # Database connection
  ├── schemas/
  │   ├── __init__.py
  │   └── schemas.py         # Pydantic models for validation
  ├── routers/
  │   ├── __init__.py
  │   ├── sensors.py         # Sensor endpoints
  │   ├── metrics.py         # Metric endpoints
  │   ├── queries.py         # Query endpoints
  │   └── test.py            # Test endpoints
  └── utils/
      ├── __init__.py
      └── helpers.py         # Helper functions
```

## Known Missing considerations
Due to time constraints, the following features were not implemented:
1. The API does not have authentication or authorization mechanisms. This is a critical feature for production APIs.
2. The API does not have rate limiting or throttling. This is important to prevent abuse and ensure fair usage.
3. Certain sections of code could be more concise.
4. Support for multiple timestamp formats.

## Installation and Running

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Initialize the database (recommended before first run):
   ```
   python -m src.database.init_db
   ```
4. Run the application:
   ```
   uvicorn src.main:app --reload
   ```
5. Access the API documentation at `http://localhost:8000/docs`

## Logging

The application includes a comprehensive logging system:

- Logs are stored in the `logs/` directory
- The main log file is `weather_api.log`
- Logs are rotated when they reach 10MB (up to 5 backup files)
- Console output shows minimal information while the log file contains detailed information

You can view the logs to diagnose issues:
```
tail -f logs/weather_api.log
```

## API Endpoints

### Sensors

- `POST /sensors/` - Create a new sensor
- `GET /sensors/` - List all sensors
- `GET /sensors/{sensor_id}` - Get a specific sensor

### Metrics

- `POST /metrics/` - Record a new metric value
- `GET /metrics/` - List metric values (can filter by sensor)

### Queries

- `POST /query/` - Query metrics with advanced filtering
- `GET /sensors/{sensor_id}/weekly-averages/` - Get the average temperature and humidity for a specific sensor in the last week

### Testing

- `POST /test/create-sample-data/` - Create a test sensor with sample data

## Quick Start

The fastest way to get started and test the API is to:

1. Start the server: `uvicorn src.main:app --reload`
2. Create sample data by making a POST request to the test endpoint:
   ```bash
   curl -X POST http://localhost:8000/test/create-sample-data/
   ```
3. This will return a JSON response with a sensor ID
4. To list all sensors:
   - `http://localhost:8000/sensors/`
5. Use this sensor ID to test other endpoints, for example:
   - `http://localhost:8000/sensors/{sensor_id}/weekly-averages/`
   - `http://localhost:8000/metrics/?sensor_id={sensor_id}`

## Example Usage

### Register a new sensor

```bash
curl -X POST http://localhost:8000/sensors/ -H "Content-Type: application/json" 
-d "{\"name\": \"Garden Sensor\", \"location\": \"Backyard\"}"
```

### Record temperature

```bash
curl -X POST http://localhost:8000/metrics/ -H "Content-Type: application/json" 
-d "{\"sensor_id\": 1, \"metric_type\": \"temperature\", \"value\": 23.5}"
```

### Query average temperature for past week

```bash
curl -X GET http://localhost:8000/sensors/1/weekly-averages/?metrics=temperature
```

### Advanced query

Query average temperature for the past month:
```bash
curl -X POST http://localhost:8000/query/ -H "Content-Type: application/json" 
-d "{\"sensor_ids\": [1], \"metric_types\": [\"temperature\"], \"statistic\": \"avg\", 
\"start_date\": \"2025-02-07T00:00:00+00:00\", \"end_date\": \"2025-03-08T00:00:00+00:00\"}"
```
Query all sensors for the minimum temperature found in the last 3 weeks:
```bash
curl -X POST http://localhost:8000/query/ -H "Content-Type: application/json" 
-d "{\"metric_types\": [\"temperature\"], \"statistic\": \"min\", \"start_date\": \"2025-02-16T00:00:00+00:00\", 
\"end_date\": \"2025-03-09T00:00:00+00:00\"}"
```

## Testing

The project includes both unit tests and integration tests.

### Unit Tests

Unit tests verify individual components in isolation:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all unit tests
pytest tests/

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=src
```

See the tests/README.md file for more details on unit testing.

### Integration Tests

Integration tests verify how components work together through the full API flow:

```bash
# Run all integration tests
pytest integration_tests/

# Run specific integration test files
pytest integration_tests/test_sensor_workflow.py
```

Integration tests use a temporary database and test the complete request-response cycle.
See the integration_tests/README.md file for more details on integration testing.
```