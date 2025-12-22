from typing import Optional, TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Project


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
