from fastapi import FastAPI

from src.routes import router as glacier_router

app = FastAPI()

app.include_router(glacier_router, prefix="/v1")


@app.get("/")
async def read_root():
    return {"Hello": "World"}
