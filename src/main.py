from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.glacier import router as glacier_router
from src.routes.project import router as project_router
from src.routes.scene import router as scene_router
from src.routes.data import router as data_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pi",
        "https://100.109.8.16",
        "https://pi.tail30e7da.ts.net",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "PATCH"],
    allow_headers=["*"],
    expose_headers=["x-total-count"],
)

app.include_router(project_router, prefix="/v1/project", tags=["Projects"])
app.include_router(glacier_router, prefix="/v1/glacier", tags=["Glaciers"])
app.include_router(scene_router, prefix="/v1/scene", tags=["Scenes"])
app.include_router(data_router, prefix="/v1/data", tags=["Data"])
