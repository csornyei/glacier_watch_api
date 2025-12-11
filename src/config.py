import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

CRS = "EPSG:32633"


@dataclass
class Config:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./glacier_watch.db")
    api_key: str = os.getenv("API_KEY", "default_api_key")


config = Config()
