import json

from fastapi import APIRouter, Depends, HTTPException

from src.controller.glacier import (
    fetch_glacier_area,
    fetch_glacier_details,
    fetch_glacier_timeseries,
)
from src.db import get_db_session
from src.logger import get_logger
from src.schemas.glacier import (
    GlacierDetailsOut,
    GlacierTimeSeriesDataPoint,
    GlacierTimeSeriesOut,
)

router = APIRouter()

logger = get_logger("glacier_watch")


@router.get(
    "/{glacier_id}",
    name="Get Glacier Details",
    response_model=GlacierDetailsOut,
)
async def get_glacier_details(
    glacier_id: str = "RGI2000-v7.0-G-08-00761", db=Depends(get_db_session)
):
    logger.info(f"Fetching glacier details for glacier_id={glacier_id}")
    glacier = await fetch_glacier_details(db, glacier_id)
    if not glacier:
        raise HTTPException(status_code=404, detail="Glacier not found")

    result = GlacierDetailsOut(
        glacier_id=glacier.glacier_id,
        name=glacier.name,
        area_m2=glacier.area_m2,
        geometry=json.loads(glacier.geometry_geojson),
    )

    logger.info(f"Returning glacier details for glacier_id={glacier_id}")
    return result


@router.get(
    "/{glacier_id}/timeseries",
    name="Get Glacier Snow Data Timeseries",
    response_model=GlacierTimeSeriesOut,
)
async def get_glacier_timeseries(glacier_id: str, db=Depends(get_db_session)):
    logger.info(f"Fetching glacier timeseries for glacier_id={glacier_id}")

    glacier_area_m2 = await fetch_glacier_area(db, glacier_id)

    if not glacier_area_m2:
        logger.error(f"Glacier not found for glacier_id={glacier_id}")
        raise HTTPException(status_code=404, detail="Glacier not found")

    snow_data = await fetch_glacier_timeseries(db, glacier_id)

    timeseries = []
    for glacier_snow_data, acquisition_date in snow_data:
        timeseries.append(
            GlacierTimeSeriesDataPoint(
                acquisition_date=acquisition_date,
                snow_area_m2=glacier_snow_data.snow_area_m2,
                snow_area_fraction=glacier_snow_data.snow_area_m2 / glacier_area_m2,
                snowline_elevation_m=glacier_snow_data.snowline_elevation_m,
            )
        )

    logger.info(
        f"Returning glacier timeseries for glacier_id={glacier_id}, found {len(timeseries)} records"
    )

    return GlacierTimeSeriesOut(
        glacier_id=glacier_id,
        timeseries=timeseries,
    )
