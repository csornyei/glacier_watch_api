from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.shared import GeoJSON


class GlacierListItem(BaseModel):
    glacier_id: str = Field(..., description="Unique identifier for the glacier")
    name: Optional[str] = Field(None, description="Name of the glacier")
    point: Optional[tuple[float, float]] = Field(
        None,
        description="Coordinates of a point within the glacier geometry [latitude, longitude]",
    )


class GlacierDetailsOut(BaseModel):
    glacier_id: str = Field(..., description="Unique identifier for the glacier")
    name: Optional[str] = Field(None, description="Name of the glacier")
    area_m2: Optional[float] = Field(
        None, description="Area of the glacier in square meters"
    )
    geometry: Optional[GeoJSON] = Field(
        None, description="GeoJSON representation of the glacier geometry"
    )


class GlacierTimeSeriesDataPoint(BaseModel):
    acquisition_date: datetime = Field(
        ..., description="Date when the data was acquired"
    )
    snow_area_m2: Optional[float] = Field(
        None, description="Area of snow coverage on the glacier in square meters"
    )
    snow_area_fraction: Optional[float] = Field(
        None, description="Fraction of the glacier area covered by snow"
    )
    snowline_elevation_m: Optional[float] = Field(
        None, description="Elevation of the snowline on the glacier in meters"
    )


class GlacierTimeSeriesOut(BaseModel):
    glacier_id: str = Field(..., description="Unique identifier for the glacier")
    timeseries: list[GlacierTimeSeriesDataPoint] = Field(
        ..., description="List of glacier snow data timeseries points"
    )
