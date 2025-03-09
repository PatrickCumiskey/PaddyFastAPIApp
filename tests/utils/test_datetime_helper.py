"""
Unit tests for the datetime_helper module.
"""
from datetime import datetime, timezone

from freezegun import freeze_time

from src.utils.datetime_helper import utc_now, get_date_range


def test_utc_now():
    """Test that utc_now() returns a timezone-aware datetime in UTC."""
    # Get current time using our helper
    now = utc_now()

    # Verify it's a datetime object
    assert isinstance(now, datetime)

    # Verify it has timezone info
    assert now.tzinfo is not None

    # Verify it's UTC timezone
    assert now.tzinfo == timezone.utc


@freeze_time("2023-07-15 12:00:00", tz_offset=0)
def test_utc_now_frozen_time():
    """Test utc_now() with frozen time to ensure predictable results."""
    # With freezegun, time should be frozen at the specified point
    now = utc_now()

    # Verify the frozen time
    expected = datetime(2023, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert now == expected


def test_get_date_range():
    """Test that get_date_range() returns correct start and end dates."""
    # Test with 7 days ago
    start_date, end_date = get_date_range(days_ago=7)

    # Verify both are datetime objects
    assert isinstance(start_date, datetime)
    assert isinstance(end_date, datetime)

    # Verify both have timezone info
    assert start_date.tzinfo is not None
    assert end_date.tzinfo is not None

    # Verify end_date is approximately now
    now = utc_now()
    assert abs((end_date - now).total_seconds()) < 1  # Less than 1 second difference

    # Verify start_date is 7 days before end_date
    delta = end_date - start_date
    assert delta.days == 7

    # Test with a different number of days
    start_date_3d, end_date_3d = get_date_range(days_ago=3)
    delta_3d = end_date_3d - start_date_3d
    assert delta_3d.days == 3


@freeze_time("2023-07-15 12:00:00", tz_offset=0)
def test_get_date_range_frozen_time():
    """Test get_date_range() with frozen time for predictable results."""
    # Test with 7 days ago
    start_date, end_date = get_date_range(days_ago=7)

    # With frozen time, we can assert exact datetimes
    expected_end = datetime(2023, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
    expected_start = datetime(2023, 7, 8, 12, 0, 0, tzinfo=timezone.utc)

    assert end_date == expected_end
    assert start_date == expected_start