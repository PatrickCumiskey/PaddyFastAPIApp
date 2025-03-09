"""
Utility functions for handling datetime operations with timezone awareness.
"""
from datetime import datetime, timezone, timedelta

def utc_now():
    """
    Returns the current UTC time as a timezone-aware datetime object.
    Replacement for the deprecated datetime.utcnow().
    """
    return datetime.now(timezone.utc)

def get_date_range(days_ago):
    """
    Return a tuple of (start_date, end_date) where:
    - end_date is now in UTC
    - start_date is days_ago days before end_date
    Both returned as timezone-aware datetime objects.
    """
    end_date = utc_now()
    start_date = end_date - timedelta(days=days_ago)
    return start_date, end_date