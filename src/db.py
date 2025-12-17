# app/db.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import config
from src.logger import get_logger

logger = get_logger("glacier_watch.db")

logger.debug("Connecting to database")

engine = create_async_engine(
    config.database_url, echo=False, pool_pre_ping=True, future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
