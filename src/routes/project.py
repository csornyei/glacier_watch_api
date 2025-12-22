from fastapi import APIRouter, Depends, HTTPException, Response

from src.controller.glacier import fetch_glacier_in_geometry, glacier_rows_to_list_items
from src.controller.project import (
    fetch_project_row,
    fetch_projects,
    fetch_projects_bounds,
)
from src.controller.scene import count_scenes_by_project_id, fetch_scenes_by_project_id
from src.db import get_db_session
from src.logger import get_logger
from src.schemas.project import ListProjectsOut, ProjectDetailsOut, ProjectList
from src.utils.geo import bounds_from_minmax, geojson_point_to_latlng, geojson_to_model

router = APIRouter()

logger = get_logger("glacier_watch")


@router.get(
    "/",
    name="List Projects",
    response_model=ListProjectsOut,
)
async def list_projects(db=Depends(get_db_session)):
    logger.info("Fetching list of projects")
    projects = await fetch_projects(db)

    bounds = await fetch_projects_bounds(db)

    logger.info(f"Fetched {len(projects)} projects")

    projects = [
        ProjectList(
            project_id=project.project_id,
            name=project.name,
            point=geojson_point_to_latlng(project.center_geojson),
        )
        for project in projects
    ]

    response = ListProjectsOut(
        projects=projects,
        map_bounds=bounds_from_minmax(
            bounds.min_lat, bounds.min_lon, bounds.max_lat, bounds.max_lon
        ),
    )

    return response


@router.get(
    "/{project_id}",
    name="Get Project Details",
    response_model=ProjectDetailsOut,
)
async def get_project_details(
    response: Response,
    project_id: str,
    db=Depends(get_db_session),
    limit: int = 100,
    offset: int = 0,
):
    logger.info(f"Fetching project details for project_id={project_id}")

    project = await fetch_project_row(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    aoi = geojson_to_model(project.aoi)
    center = geojson_point_to_latlng(project.center_geojson)
    bounds = bounds_from_minmax(
        project.min_lat, project.min_lon, project.max_lat, project.max_lon
    )

    glacier_rows = await fetch_glacier_in_geometry(db, project.area_of_interest)
    glaciers = glacier_rows_to_list_items(glacier_rows)

    logger.info(f"Fetched {len(glaciers)} glaciers for project_id={project_id}")

    scenes = await fetch_scenes_by_project_id(db, project_id, limit, offset)

    logger.info(f"Fetched {len(scenes)} scenes for project_id={project_id}")

    total_scenes = await count_scenes_by_project_id(db, project_id)
    logger.info(
        f"Total scenes for project_id={project_id}: {total_scenes} (limit={limit}, offset={offset})"
    )

    response.headers["X-Total-Count"] = str(total_scenes)

    return {
        "project": {
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "aoi": aoi,
            "glaciers": glaciers,
            "scenes": scenes,
        },
        "map_center": center,
        "map_bounds": bounds,
        "scene_total_count": total_scenes,
    }
