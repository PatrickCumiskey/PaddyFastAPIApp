from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import func

from src.models.models import Metric
from src.schemas.schemas import StatisticType, create_query_result


def generate_timestamp_range(start_date: datetime, end_date: datetime, interval_hours: int = 3) -> List[datetime]:
    """
    Generate a list of timestamps from start_date to end_date at specified intervals

    Args:
        start_date (datetime): The starting datetime
        end_date (datetime): The ending datetime
        interval_hours (int): Hours between each timestamp

    Returns:
        List[datetime]: List of timestamps
    """
    timestamps = []
    current = start_date
    while current <= end_date:
        timestamps.append(current)
        current += timedelta(hours=interval_hours)
    return timestamps


def get_sample_metric_ranges() -> Dict[str, Tuple[float, float]]:
    """
    Get reasonable value ranges for each metric type

    Returns:
        Dict[str, Tuple[float, float]]: Dictionary mapping metric types to min/max value ranges
    """
    return {
        "temperature": (10.0, 35.0),  # °C
        "humidity": (30.0, 90.0),  # %
        "wind_speed": (0.0, 25.0),  # km/h
        "pressure": (990.0, 1020.0),  # hPa
        "rainfall": (0.0, 15.0)  # mm
    }

def get_statistic_query(metric_query, statistic):
    """
    Retrieve a specific statistic from a metric query.

    Args:
        metric_query: SQLAlchemy query object for Metric entities
        statistic: The type of statistic to retrieve (from StatisticType enum)

    Returns:
        Query result with the requested statistic

    Raises:
        ValueError: If an unsupported statistic type is provided
    """
    # Dictionary mapping statistic types to their corresponding functions
    statistic_functions = {
        StatisticType.MIN: lambda q: q.with_entities(Metric.sensor_id, func.min(Metric.value).label("value")).first(),
        StatisticType.MAX: lambda q: q.with_entities(Metric.sensor_id, func.max(Metric.value).label("value")).first(),
        StatisticType.SUM: lambda q: q.with_entities(func.sum(Metric.value).label("value")).first(),
        StatisticType.AVG: lambda q: q.with_entities(func.avg(Metric.value).label("value")).first(),
    }

    if statistic not in statistic_functions:
        raise ValueError(f"Unsupported statistic type: {statistic}")

    return statistic_functions[statistic](metric_query)

def create_query_result_object(statistic, metric_type, value, sensor_ids, start_date, end_date, sensor_id=None):
    if statistic in ("min", "max"):
        return create_query_result(
            statistic=statistic,
            sensor_id=sensor_id,
            metric_type=metric_type,
            value=value,
            start_date=start_date,
            end_date=end_date
        )
    else:
        return create_query_result(
            statistic=statistic,
            sensor_ids=sensor_ids if sensor_ids else [],
            metric_type=metric_type,
            value=value,
            start_date=start_date,
            end_date=end_date
        )