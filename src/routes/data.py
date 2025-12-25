import shutil

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from src.config import config
from src.logger import get_logger
import src.controller.data as data_controller

router = APIRouter()

logger = get_logger("glacier_watch")


@router.get("/raw/")
def get_raw_project_folders():
    try:
        logger.info("Fetching raw project folders")

        raw_folder = config.data_folder_path / "raw"
        raw_folder.mkdir(parents=True, exist_ok=True)

        contents, size = data_controller.get_folder_contents(raw_folder)
        logger.info(f"Raw folder contents: {contents}, size: {size} bytes")

        return {
            "contents": contents,
            "size": data_controller.bytes_to_readable(size),
        }
    except Exception as e:
        logger.error(f"Error fetching raw project folders: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/raw/{project_id}")
def get_raw_project_folder(project_id: str):
    try:
        logger.info(f"Fetching raw data for project folder: {project_id}")

        folder_path = config.data_folder_path / "raw" / project_id
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(f"Project folder '{project_id}' does not exist")
            raise HTTPException(status_code=404, detail="Project folder not found")

        content, size = data_controller.get_folder_contents(folder_path)
        logger.info(
            f"Project folder '{project_id}' contents: {content}, size: {size} bytes"
        )

        return {
            "contents": content,
            "size": data_controller.bytes_to_readable(size),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project folder '{project_id}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/raw/{project_id}/{folder_name}")
def get_raw_folder_contents(project_id: str, folder_name: str):
    try:
        logger.info(
            f"Fetching contents of folder '{folder_name}' for project '{project_id}'"
        )

        folder_path = config.data_folder_path / "raw" / project_id / folder_name
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(
                f"Folder '{folder_name}' for project '{project_id}' does not exist"
            )
            raise HTTPException(status_code=404, detail="Folder not found")

        contents, size = data_controller.get_folder_contents(folder_path)
        logger.info(
            f"Contents of folder '{folder_name}' for project '{project_id}': {contents}, size: {size} bytes"
        )

        return {
            "contents": contents,
            "size": data_controller.bytes_to_readable(size),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching contents of folder '{folder_name}' for project '{project_id}': {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/raw/{project_id}/{folder_name}")
def delete_raw_folder(project_id: str, folder_name: str):
    try:
        logger.info(f"Deleting folder '{folder_name}' for project '{project_id}'")

        folder_path = config.data_folder_path / "raw" / project_id / folder_name
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(
                f"Folder '{folder_name}' for project '{project_id}' does not exist"
            )
            raise HTTPException(status_code=404, detail="Folder not found")

        shutil.rmtree(folder_path)
        logger.info(
            f"Folder '{folder_name}' for project '{project_id}' deleted successfully"
        )

        return {"message": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting folder '{folder_name}' for project '{project_id}': {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/result")
def get_processed_results():
    try:
        logger.info("Fetching processed results data")

        result_folder = config.data_folder_path / "result"
        result_folder.mkdir(parents=True, exist_ok=True)

        contents, size = data_controller.get_folder_contents(result_folder)
        logger.info(f"Result folder contents: {contents}, size: {size} bytes")

        return {
            "contents": contents,
            "size": data_controller.bytes_to_readable(size),
        }
    except Exception as e:
        logger.error(f"Error fetching processed results data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/result/{project_id}")
def get_processed_results_for_project(project_id: str):
    try:
        logger.info(f"Fetching processed results for project: {project_id}")

        folder_path = config.data_folder_path / "result" / project_id
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(f"Result folder for project '{project_id}' does not exist")
            raise HTTPException(status_code=404, detail="Result folder not found")

        contents, size = data_controller.get_folder_contents(folder_path)
        logger.info(
            f"Result folder for project '{project_id}' contents: {contents}, size: {size} bytes"
        )

        return {
            "contents": contents,
            "size": data_controller.bytes_to_readable(size),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching result folder for project '{project_id}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/result/{project_id}/{folder_name}")
def get_result_folder_contents(project_id: str, folder_name: str):
    try:
        logger.info(
            f"Fetching contents of result folder '{folder_name}' for project '{project_id}'"
        )

        folder_path = config.data_folder_path / "result" / project_id / folder_name
        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(
                f"Result folder '{folder_name}' for project '{project_id}' does not exist"
            )
            raise HTTPException(status_code=404, detail="Folder not found")

        contents, size = data_controller.get_folder_contents(folder_path)
        logger.info(
            f"Contents of result folder '{folder_name}' for project '{project_id}': {contents}, size: {size} bytes"
        )

        return {
            "contents": contents,
            "size": data_controller.bytes_to_readable(size),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching contents of result folder '{folder_name}' for project '{project_id}': {e}"
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/result/{project_id}/{folder_name}/{file_name}", response_class=FileResponse
)
def download_result_file(project_id: str, folder_name: str, file_name: str):
    base_dir = (config.data_folder_path / "result").resolve()
    folder_path = (
        config.data_folder_path / "result" / project_id / folder_name
    ).resolve()
    file_path = (folder_path / file_name).resolve()

    if base_dir not in file_path.parents:
        logger.warning(
            f"Attempted path traversal attack detected for file '{file_name}' in folder '{folder_name}' for project '{project_id}'"
        )
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not file_path.exists() or not file_path.is_file():
        logger.warning(
            f"File '{file_name}' in folder '{folder_name}' for project '{project_id}' does not exist"
        )
        raise HTTPException(status_code=404, detail="File not found")

    logger.info(
        f"Downloading file '{file_name}' from folder '{folder_name}' for project '{project_id}'"
    )

    return file_path
