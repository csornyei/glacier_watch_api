from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.glacier import GlacierListItem
from src.schemas.scene import SceneListItem
from src.schemas.shared import GeoJSON


class ProjectListItem(BaseModel):
    project_id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")


class ProjectList(ProjectListItem):
    point: Optional[tuple[float, float]] = Field(
        None,
        description="Coordinates of a point within the project's area of interest [latitude, longitude]",
    )


class ProjectCreateIn(BaseModel):
    project_id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(
        None, description="Detailed description of the project"
    )
    aoi: Optional[GeoJSON] = Field(
        None, description="GeoJSON representation of the project's area of interest"
    )
    bands: list[str] = Field(
        ..., description="List of spectral bands relevant to the project", min_length=1
    )


class ListProjectsOut(BaseModel):
    projects: list[ProjectList] = Field(
        ..., description="List of projects with basic information"
    )
    map_bounds: Optional[tuple[tuple[float, float], tuple[float, float]]] = Field(
        None,
        description="Latitude and longitude of the bounding box of all projects' areas of interest (min_lat - S, min_lon - W), (max_lat - N, max_lon - E)",
    )


class ProjectDetails(ProjectListItem):
    description: str = Field(..., description="Detailed description of the project")
    aoi: Optional[GeoJSON] = Field(
        None, description="GeoJSON representation of the project's area of interest"
    )
    glaciers: list[GlacierListItem] = Field(
        ..., description="List of glaciers associated with the project"
    )
    scenes: list[SceneListItem] = Field(
        ..., description="List of scenes associated with the project"
    )


class ProjectDetailsOut(BaseModel):
    project: ProjectDetails = Field(
        ..., description="Detailed information about the project"
    )
    map_center: Optional[tuple[float, float]] = Field(
        None,
        description="Latitude and longitude of the center point of the project's area of interest",
    )
    map_bounds: Optional[tuple[tuple[float, float], tuple[float, float]]] = Field(
        None,
        description="Latitude and longitude of the bounding box of the project's area of interest (min_lat - S, min_lon - W), (max_lat - N, max_lon - E)",
    )
    scene_total_count: int = Field(
        ..., description="Total number of scenes associated with the project"
    )


class ProjectConfig(BaseModel):
    bands: list[str] = Field(
        ..., description="List of spectral bands relevant to the project", min_length=1
    )
    project_id: str = Field(..., description="Unique identifier for the project")
    min_coverage_percent: Optional[int] = Field(
        60,
        description="Minimum coverage percentage for scenes to be included in the project",
    )
