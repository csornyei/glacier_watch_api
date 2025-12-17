from typing import Any, Literal

from pydantic import BaseModel, Field


class GeoJSON(BaseModel):
    type: Literal[
        "Point",
        "LineString",
        "Polygon",
        "MultiPoint",
        "MultiLineString",
        "MultiPolygon",
    ] = Field(..., description="Type of the GeoJSON object, e.g., 'Point'")
    coordinates: Any = Field(
        ..., description="Coordinates of the point [longitude, latitude]"
    )
