from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.models import Metric, Sensor
from src.schemas.schemas import (
    QueryParams, SingleSensorQueryResult,
    MultiSensorQueryResult,
    MetricType
)
from src.utils.datetime_helper import get_date_range
from src.utils.helpers import get_statistic_query, create_query_result_object
from src.utils.logging_config import logger

router = APIRouter(
    tags=["queries"]
)

@router.post("/query/", response_model=List[Union[SingleSensorQueryResult, MultiSensorQueryResult]])
def query_metrics(query_params: QueryParams, db: Session = Depends(get_db)):
    try:
        query = db.query(Metric)

        if query_params.sensor_ids:
            query = query.filter(Metric.sensor_id.in_(query_params.sensor_ids))

        if query_params.start_date and query_params.end_date:
            query = query.filter(
                Metric.timestamp >= query_params.start_date,
                Metric.timestamp <= query_params.end_date
            )
        else:
            start_date, end_date = get_date_range(days_ago=1)
            query = query.filter(Metric.timestamp >= start_date)

        results = []

        for metric_type in query_params.metric_types:
            try:
                metric_query = query.filter(Metric.metric_type == metric_type)

                if not metric_query.first():
                    logger.info(f"No data found for metric type: {metric_type}")
                    continue

                stat_result = get_statistic_query(metric_query, query_params.statistic)

                if stat_result and stat_result.value is not None:
                    included_sensors = [
                        sensor_id[0] for sensor_id in
                        metric_query.with_entities(Metric.sensor_id).distinct().all()
                    ]

                    query_result = create_query_result_object(
                        query_params.statistic.value,
                        metric_type.value,
                        stat_result.value,
                        included_sensors,
                        query_params.start_date,
                        query_params.end_date,
                        sensor_id=stat_result.sensor_id if query_params.statistic in ("min", "max") else None
                    )
                    results.append(query_result)
            except SQLAlchemyError as e:
                logger.error(f"Error processing metric {metric_type}: {str(e)}")

        if not results:
            logger.info("Query returned no results")

        return results
    except SQLAlchemyError as e:
        logger.error(f"Database error in query endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="A database error occurred. This might be due to missing tables or connection issues."
        )

@router.get("/sensors/{sensor_id}/weekly-averages/")
def get_weekly_averages(
        sensor_id: int,
        metrics: List[MetricType] = Query(default=[MetricType.TEMPERATURE, MetricType.HUMIDITY]),
        db: Session = Depends(get_db)
):
    try:
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if sensor is None:
            raise HTTPException(status_code=404, detail="Sensor not found")

        start_date, end_date = get_date_range(days_ago=7)

        results = []

        for metric_type in metrics:
            try:
                avg_value = db.query(func.avg(Metric.value).label("average")).filter(
                    Metric.sensor_id == sensor_id,
                    Metric.metric_type == metric_type,
                    Metric.timestamp >= start_date,
                    Metric.timestamp <= end_date
                ).scalar()

                if avg_value is not None:
                    result = MultiSensorQueryResult(
                        sensor_ids=[sensor_id],
                        metric_type=metric_type.value,
                        statistic="avg",
                        value=avg_value,
                        start_date=start_date,
                        end_date=end_date
                    )
                    results.append(result.model_dump())
                else:
                    result = {
                        "sensor_ids": [sensor_id],
                        "metric_type": metric_type,
                        "statistic": "avg",
                        "value": None,
                        "start_date": start_date,
                        "end_date": end_date,
                        "message": "No data available for this metric in the specified time range"
                    }
                    results.append(result)
            except SQLAlchemyError as e:
                logger.error(f"Database error in weekly averages for {metric_type}: {str(e)}")
                result = {
                    "sensor_ids": [sensor_id],
                    "metric_type": metric_type,
                    "statistic": "avg",
                    "value": None,
                    "start_date": start_date,
                    "end_date": end_date,
                    "error": "An error occurred while retrieving this metric"
                }
                results.append(result)

        if not results:
            return {"message": "No data available for the specified metrics and time range"}

        return results
    except SQLAlchemyError as e:
        logger.error(f"Database error in weekly averages endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="A database error occurred. This might be due to missing tables or connection issues."
        )