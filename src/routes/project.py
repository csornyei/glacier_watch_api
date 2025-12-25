import shutil
from fastapi import APIRouter, Depends, HTTPException, Response

from src.controller.glacier import fetch_glacier_in_geometry, glacier_rows_to_list_items
import src.controller.project as project_controller
from src.controller.scene import count_scenes_by_project_id, fetch_scenes_by_project_id
from src.db import get_db_session
from src.logger import get_logger
from src.schemas.project import (
    ListProjectsOut,
    ProjectDetailsOut,
    ProjectList,
    ProjectCreateIn,
    ProjectListItem,
)
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
    projects = await project_controller.fetch_projects(db)

    bounds = await project_controller.fetch_projects_bounds(db)

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


@router.post(
    "/",
    name="Add Project",
    response_model=ProjectListItem,
)
async def add_project(project_data: ProjectCreateIn, db=Depends(get_db_session)):
    try:
        existing_project = await project_controller.fetch_project_row(
            db, project_data.project_id
        )

        if existing_project:
            raise HTTPException(status_code=400, detail="Project ID already exists")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking existing project: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    project_folder_path = None
    try:
        logger.info(f"Creating project with ID: {project_data.project_id}")

        project_folder_path = project_controller.create_project_folder(
            project_data.project_id
        )

        config_content = {
            "project_id": project_data.project_id,
            "bands": project_data.bands,
        }

        project_controller.save_project_config(project_folder_path, config_content)

        logger.info(f"Project folder and config created at: {project_folder_path}")

        project = await project_controller.create_project(
            db,
            project_id=project_data.project_id,
            name=project_data.name,
            description=project_data.description,
            area_of_interest=project_data.aoi,
        )

        logger.info(f"Project {project_data.project_id} created successfully in DB")

        return ProjectListItem(project_id=project.project_id, name=project.name)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating project: {e}")

        if project_folder_path and project_folder_path.exists():
            shutil.rmtree(project_folder_path)
            logger.info(f"Cleaned up project folder at: {project_folder_path}")

        raise HTTPException(status_code=500, detail="Failed to create project")


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

    project = await project_controller.fetch_project_row(db, project_id)

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
