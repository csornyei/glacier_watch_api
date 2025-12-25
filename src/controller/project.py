import yaml
from pathlib import Path
from typing import Optional, TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from src.models import Project
from src.schemas.shared import GeoJSON
from src.config import config


class ProjectRow(TypedDict):
    project_id: str
    name: str
    description: Optional[str]
    area_of_interest: Optional[str]
    aoi: Optional[str]
    center_geojson: Optional[str]
    min_lon: Optional[float]
    min_lat: Optional[float]
    max_lon: Optional[float]
    max_lat: Optional[float]


async def fetch_projects(db: AsyncSession) -> list:
    project_rows = await db.execute(
        select(
            Project.project_id,
            Project.name,
            func.ST_AsGeoJSON(func.ST_PointOnSurface(Project.area_of_interest)).label(
                "center_geojson"
            ),
        )
    )

    return [row for row in project_rows.all()]


async def fetch_projects_bounds(db):
    res = await db.execute(
        select(
            func.ST_XMin(func.ST_Extent(Project.area_of_interest)).label("min_lon"),
            func.ST_YMin(func.ST_Extent(Project.area_of_interest)).label("min_lat"),
            func.ST_XMax(func.ST_Extent(Project.area_of_interest)).label("max_lon"),
            func.ST_YMax(func.ST_Extent(Project.area_of_interest)).label("max_lat"),
        ).where(Project.area_of_interest.isnot(None))
    )

    return res.first()


async def fetch_project_row(db: AsyncSession, project_id: str) -> ProjectRow:
    project_result = await db.execute(
        select(
            Project.project_id,
            Project.name,
            Project.description,
            Project.area_of_interest,
            func.ST_AsGeoJSON(Project.area_of_interest).label("aoi"),
            func.ST_AsGeoJSON(func.ST_PointOnSurface(Project.area_of_interest)).label(
                "center_geojson"
            ),
            func.ST_XMin(Project.area_of_interest).label("min_lon"),
            func.ST_YMin(Project.area_of_interest).label("min_lat"),
            func.ST_XMax(Project.area_of_interest).label("max_lon"),
            func.ST_YMax(Project.area_of_interest).label("max_lat"),
        ).filter(Project.project_id == project_id)
    )

    return project_result.first()


def create_project_folder(project_id: str) -> Path:
    base_path = config.data_folder_path

    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)

    project_path = base_path / project_id

    project_path.mkdir(parents=True, exist_ok=True)

    return project_path


def save_project_config(project_path: Path, config_data: dict):
    config_path = project_path / "config.yaml"

    with open(config_path, "w") as config_file:
        yaml.dump(config_data, config_file)


async def create_project(
    db: AsyncSession,
    project_id: str,
    name: str,
    description: Optional[str] = None,
    area_of_interest: Optional[GeoJSON] = None,
) -> Project:
    geom = None
    if area_of_interest:
        geom = from_shape(shape(area_of_interest.model_dump()), srid=4326)

    new_project = Project(
        project_id=project_id,
        name=name,
        description=description,
        area_of_interest=geom,
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return new_project
