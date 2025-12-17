from fastapi import FastAPI

from src.routes.glacier import router as glacier_router
from src.routes.project import router as project_router
from src.routes.scene import router as scene_router

app = FastAPI()

app.include_router(project_router, prefix="/v1/project", tags=["Projects"])
app.include_router(glacier_router, prefix="/v1/glacier", tags=["Glaciers"])
app.include_router(scene_router, prefix="/v1/scene", tags=["Scenes"])
