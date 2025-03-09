from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src.schemas.schemas import (
    SingleSensorQueryResult,
    MultiSensorQueryResult,
    StatisticType
)
from src.utils.helpers import (
    generate_timestamp_range,
    get_sample_metric_ranges,
    get_statistic_query,
    create_query_result_object
)


def test_generate_timestamp_range():
    """Test the generate_timestamp_range helper function"""
    # Test with 3-hour intervals (default)
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 1, 1, 12, 0, 0)

    timestamps = generate_timestamp_range(start, end)

    # Should have 5 timestamps: 0, 3, 6, 9, 12
    assert len(timestamps) == 5
    assert timestamps[0] == start
    assert timestamps[-1] == end

    # Check intervals
    for i in range(1, len(timestamps)):
        diff = timestamps[i] - timestamps[i - 1]
        assert diff == timedelta(hours=3)

    # Test with custom interval
    timestamps = generate_timestamp_range(start, end, interval_hours=6)

    # Should have 3 timestamps: 0, 6, 12
    assert len(timestamps) == 3
    assert timestamps[0] == start
    assert timestamps[1] == start + timedelta(hours=6)
    assert timestamps[2] == end


def test_get_sample_metric_ranges():
    """Test the get_sample_metric_ranges helper function"""
    ranges = get_sample_metric_ranges()

    # Check that we have ranges for all expected metric types
    expected_metrics = ["temperature", "humidity", "wind_speed", "pressure", "rainfall"]
    for metric in expected_metrics:
        assert metric in ranges

        # Each range should be a tuple of (min, max)
        assert isinstance(ranges[metric], tuple)
        assert len(ranges[metric]) == 2
        assert ranges[metric][0] < ranges[metric][1]

        # Values should be numerical
        assert isinstance(ranges[metric][0], (int, float))
        assert isinstance(ranges[metric][1], (int, float))


def test_get_statistic_query():
    """Test the get_statistic_query helper function"""
    # Create a mock query
    mock_query = MagicMock()
    mock_min_result = MagicMock()
    mock_min_result.sensor_id = 1
    mock_min_result.value = 10.5

    mock_max_result = MagicMock()
    mock_max_result.sensor_id = 2
    mock_max_result.value = 35.0

    mock_sum_result = MagicMock()
    mock_sum_result.value = 150.5

    mock_avg_result = MagicMock()
    mock_avg_result.value = 22.5

    # Set up mock query responses for different statistics
    mock_query.with_entities.return_value.first.side_effect = [
        mock_min_result,  # For MIN
        mock_max_result,  # For MAX
        mock_sum_result,  # For SUM
        mock_avg_result  # For AVG
    ]

    # Test MIN statistic
    result = get_statistic_query(mock_query, StatisticType.MIN)
    assert result.sensor_id == 1
    assert result.value == 10.5

    # Test MAX statistic
    result = get_statistic_query(mock_query, StatisticType.MAX)
    assert result.sensor_id == 2
    assert result.value == 35.0

    # Test SUM statistic
    result = get_statistic_query(mock_query, StatisticType.SUM)
    assert result.value == 150.5

    # Test AVG statistic
    result = get_statistic_query(mock_query, StatisticType.AVG)
    assert result.value == 22.5

    # Test invalid statistic
    with pytest.raises(ValueError):
        get_statistic_query(mock_query, "invalid_statistic")


def test_create_query_result_object():
    """Test the create_query_result_object helper function"""
    # Test with min statistic
    now = datetime.now(timezone.utc)
    min_result = create_query_result_object(
        statistic="min",
        metric_type="temperature",
        value=20.5,
        sensor_ids=[],
        sensor_id=1,
        start_date=now,
        end_date=now
    )

    # Verify it's the right type
    assert isinstance(min_result, SingleSensorQueryResult)

    # Verify all fields are set correctly
    assert min_result.sensor_id == 1
    assert min_result.metric_type == "temperature"
    assert min_result.statistic == "min"
    assert min_result.value == 20.5
    assert min_result.start_date == now
    assert min_result.end_date == now

    # Test with max statistic and no dates
    max_result = create_query_result_object(
        statistic="max",
        metric_type="humidity",
        value=85.5,
        sensor_ids=[],
        sensor_id=2,
        start_date=None,
        end_date=None
    )

    # Verify it's the right type
    assert isinstance(max_result, SingleSensorQueryResult)

    # Verify required fields are set correctly
    assert max_result.sensor_id == 2
    assert max_result.metric_type == "humidity"
    assert max_result.statistic == "max"
    assert max_result.value == 85.5

    # Test with avg statistic
    avg_result = create_query_result_object(
        statistic="avg",
        metric_type="temperature",
        value=22.5,
        sensor_ids=[1, 2, 3],
        sensor_id=None,
        start_date=now,
        end_date=now
    )

    # Verify it's the right type
    assert isinstance(avg_result, MultiSensorQueryResult)

    # Verify all fields are set correctly
    assert avg_result.sensor_ids == [1, 2, 3]
    assert avg_result.metric_type == "temperature"
    assert avg_result.statistic == "avg"
    assert avg_result.value == 22.5
    assert avg_result.start_date == now
    assert avg_result.end_date == now

    # Test with empty sensor_ids
    sum_result = create_query_result_object(
        statistic="sum",
        metric_type="rainfall",
        value=45.2,
        sensor_ids=[],
        sensor_id=None,
        start_date=None,
        end_date=None
    )

    # Verify sensor_ids is an empty list, not None
    assert isinstance(sum_result, MultiSensorQueryResult)
    assert sum_result.sensor_ids == []