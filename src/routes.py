from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from src.logger import get_logger
from src.db import get_db_session
from src.models import Glacier, Project, Scene, GlacierSnowData, SceneStatusEnum

router = APIRouter()

logger = get_logger("glacier_watch.routes")


@router.get("/project", name="List Projects", tags=["Projects"])
async def list_projects(db=Depends(get_db_session)):
    projects = await db.execute(select(Project))
    projects = projects.scalars().all()

    return {
        "projects": [{"project_id": p.project_id, "name": p.name} for p in projects]
    }


@router.get("/project/{project_id}", name="Get Project Details", tags=["Projects"])
async def get_project_details(project_id: str, db=Depends(get_db_session)):
    project_result = await db.execute(
        select(Project).filter(Project.project_id == project_id)
    )
    project = project_result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    glaciers_result = await db.execute(
        select(Glacier).filter(
            func.ST_Within(Glacier.geometry, project.area_of_interest)
        )
    )
    glaciers = glaciers_result.scalars().all()

    scenes_result = await db.execute(
        select(Scene).filter(Scene.project_id == project_id)
    )
    scenes = scenes_result.scalars().all()

    return {
        "project": {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "glaciers": [
                {"glacier_id": g.glacier_id, "name": g.name} for g in glaciers
            ],
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "acquisition_date": s.acquisition_date,
                    "status": s.status.name,
                }
                for s in scenes
            ],
        }
    }


@router.get("/glacier/{glacier_id}", name="Get Glacier Details", tags=["Glaciers"])
async def get_glacier_details(
    glacier_id: str = "RGI2000-v7.0-G-08-00761", db=Depends(get_db_session)
):
    glacier_result = await db.execute(
        select(Glacier).filter(Glacier.glacier_id == glacier_id)
    )
    glacier = glacier_result.scalars().first()
    if not glacier:
        raise HTTPException(status_code=404, detail="Glacier not found")

    return {
        "glacier": {
            "glacier_id": glacier.glacier_id,
            "name": glacier.name,
            "area_m2": glacier.area_m2,
        }
    }


@router.get(
    "/glacier/{glacier_id}/timeseries",
    name="Get Glacier Snow Data Timeseries",
    tags=["Glaciers"],
)
async def get_glacier_timeseries(glacier_id: str, db=Depends(get_db_session)):
    glacier_result = await db.execute(
        select(Glacier).filter(Glacier.glacier_id == glacier_id)
    )
    glacier = glacier_result.scalars().first()
    if not glacier:
        raise HTTPException(status_code=404, detail="Glacier not found")

    snow_select = (
        select(GlacierSnowData, Scene.acquisition_date)
        .join(Scene, GlacierSnowData.scene_id == Scene.scene_id)
        .where(GlacierSnowData.glacier_id == glacier_id)
        .order_by(GlacierSnowData.created_at)
    )

    snow_data = await db.execute(snow_select)
    snow_data = snow_data.all()

    print(snow_data)
    timeseries = []
    for glacier_snow_data, acquisition_date in snow_data:
        timeseries.append(
            {
                "snow_area_m2": glacier_snow_data.snow_area_m2,
                "snowline_elevation_m": glacier_snow_data.snowline_elevation_m,
                "snow_area_fraction": glacier_snow_data.snow_area_m2 / glacier.area_m2,
                "acquisition_date": acquisition_date,
            }
        )

    return timeseries


@router.get("/scene/{scene_id}", name="Get Scene Details", tags=["Scenes"])
async def get_scene_details(scene_id: str, db=Depends(get_db_session)):
    scene = await db.execute(select(Scene).filter(Scene.scene_id == scene_id))
    scene = scene.scalars().first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return {
        "scene": {
            "scene_id": scene.scene_id,
            "project_id": scene.project_id,
            "acquisition_date": scene.acquisition_date,
            "status": scene.status.name,
            "attempts_download": scene.attempts_download,
            "attempts_processing": scene.attempts_processing,
            "last_error": scene.last_error,
        }
    }


@router.patch(
    "/scene/{scene_id}/status/{new_status}", name="Update Scene", tags=["Scenes"]
)
async def update_scene_status(
    scene_id: str, new_status: SceneStatusEnum, db=Depends(get_db_session)
):
    scene = await db.execute(select(Scene).filter(Scene.scene_id == scene_id))
    scene = scene.scalars().first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    try:
        scene.status = new_status
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    db.add(scene)
    db.commit()
    db.refresh(scene)

    return {
        "scene": {
            "scene_id": scene.scene_id,
            "status": scene.status.name,
        }
    }
