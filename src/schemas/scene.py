from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SceneListItem(BaseModel):
    scene_id: str = Field(..., description="Unique identifier for the scene")
    acquisition_date: datetime = Field(..., description="Acquisition date of the scene")
    status: str = Field(..., description="Processing status of the scene")


class SceneDetailsOut(BaseModel):
    scene_id: str = Field(..., description="Unique identifier for the scene")
    project_id: str = Field(..., description="Identifier for the associated project")
    acquisition_date: datetime = Field(..., description="Acquisition date of the scene")
    status: str = Field(..., description="Processing status of the scene")
    attempts_download: int = Field(..., description="Number of download attempts")
    attempts_processing: int = Field(..., description="Number of processing attempts")
    last_error: Optional[str] = Field(None, description="Last error message, if any")


class ScenePatchStatusOut(BaseModel):
    scene_id: str = Field(..., description="Unique identifier for the scene")
    status: str = Field(..., description="Updated processing status of the scene")
