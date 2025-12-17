from fastapi import APIRouter, Depends, HTTPException

from src.config import config
from src.controller.scene import fetch_scene_row, update_scene_status
from src.db import get_db_session
from src.logger import get_logger
from src.models import SceneStatusEnum
from src.schemas.scene import SceneDetailsOut, ScenePatchStatusOut

router = APIRouter()

logger = get_logger("glacier_watch")


@router.get("/{scene_id}", name="Get Scene Details", response_model=SceneDetailsOut)
async def get_scene_details(scene_id: str, db=Depends(get_db_session)):
    scene = await fetch_scene_row(db, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return {
        "scene_id": scene.scene_id,
        "project_id": scene.project_id,
        "acquisition_date": scene.acquisition_date,
        "status": scene.status.name,
        "attempts_download": scene.attempts_download,
        "attempts_processing": scene.attempts_processing,
        "last_error": scene.last_error,
    }


@router.patch(
    "/{scene_id}/status/{new_status}",
    name="Update Scene Status",
    response_model=ScenePatchStatusOut,
)
async def patch_scene_status(
    scene_id: str, new_status: SceneStatusEnum, api_key: str, db=Depends(get_db_session)
):
    if api_key != config.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    scene = await fetch_scene_row(db, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    try:
        scene = await update_scene_status(db, scene, new_status)
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status value")

    return {
        "scene_id": scene.scene_id,
        "status": scene.status.name,
    }
