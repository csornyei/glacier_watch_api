from typing import Optional, TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Scene


class SceneRow(TypedDict):
    scene_id: str
    project_id: str
    status: str


async def fetch_scene_row(db: AsyncSession, scene_id: str) -> Optional[Scene]:
    scene_result = await db.execute(select(Scene).filter(Scene.scene_id == scene_id))

    return scene_result.scalar_one_or_none()


async def update_scene_status(db: AsyncSession, scene: Scene, new_status: str) -> Scene:
    scene.status = new_status
    db.add(scene)
    await db.commit()
    await db.refresh(scene)
    return scene


async def fetch_scenes_by_project_id(
    db: AsyncSession, project_id: str, limit: int, offset: int
) -> list[SceneRow]:
    scenes_result = await db.execute(
        select(Scene.scene_id, Scene.acquisition_date, Scene.status)
        .filter(Scene.project_id == project_id)
        .order_by(Scene.acquisition_date.desc())
        .limit(limit)
        .offset(offset)
    )

    return scenes_result.all()


async def count_scenes_by_project_id(db: AsyncSession, project_id: str) -> int:
    total_scenes_result = await db.execute(
        select(func.count()).select_from(Scene).filter(Scene.project_id == project_id)
    )
    return total_scenes_result.scalar_one()
