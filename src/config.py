import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CRS = "EPSG:32633"


@dataclass
class Config:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./glacier_watch.db")
    api_key: str = os.getenv("API_KEY", "default_api_key")

    data_folder_path: Path = Path(os.getenv("DATA_FOLDER_PATH", "./data")).resolve()


config = Config()
