from typing import Optional, TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import get_logger
from src.models import Glacier, GlacierSnowData, Scene
from src.schemas.glacier import GlacierListItem
from src.utils.geo import geojson_point_to_latlng

logger = get_logger("glacier_watch")


class GlacierRow(TypedDict):
    glacier_id: str
    name: str
    geometry_geojson: Optional[str]


async def fetch_glacier_area(db: AsyncSession, glacier_id: str) -> Optional[float]:
    exists = await db.execute(
        select(Glacier.area_m2).filter(Glacier.glacier_id == glacier_id)
    )
    return exists.scalar_one_or_none()


async def fetch_glacier_in_geometry(db: AsyncSession, geometry) -> list[GlacierRow]:
    glacier_result = await db.execute(
        select(
            Glacier.glacier_id,
            Glacier.name,
            func.ST_AsGeoJSON(func.ST_PointOnSurface(Glacier.geometry)).label(
                "pt_geojson"
            ),
        ).filter(func.ST_Within(Glacier.geometry, geometry))
    )

    return glacier_result.all()


async def fetch_glacier_details(db: AsyncSession, glacier_id: str):
    glacier_result = await db.execute(
        select(
            Glacier.glacier_id,
            Glacier.name,
            func.ST_AsGeoJSON(Glacier.geometry).label("geometry_geojson"),
        ).filter(Glacier.glacier_id == glacier_id)
    )

    logger.info(f"Fetched glacier details for glacier_id={glacier_id}")

    return glacier_result.first()


async def fetch_glacier_timeseries(db: AsyncSession, glacier_id: str):
    snow_select = (
        select(GlacierSnowData, Scene.acquisition_date)
        .join(Scene, GlacierSnowData.scene_id == Scene.scene_id)
        .where(GlacierSnowData.glacier_id == glacier_id)
        .order_by(GlacierSnowData.created_at)
    )

    snow_data = await db.execute(snow_select)
    snow_data = snow_data.all()

    return snow_data


def __glacier_row_to_list_item(glacier: GlacierRow) -> GlacierListItem:
    return {
        "glacier_id": glacier.glacier_id,
        "name": glacier.name,
        "point": geojson_point_to_latlng(glacier.pt_geojson),
    }


def glacier_rows_to_list_items(glacier_rows: list[GlacierRow]) -> list[GlacierListItem]:
    glacier_rows.sort(
        key=lambda x: (x.name is None, (x.name or "").casefold(), x.glacier_id)
    )
    rows = [__glacier_row_to_list_item(g) for g in glacier_rows]

    return rows
