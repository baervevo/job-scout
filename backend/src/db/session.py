from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from config import settings

from src.utils.logger import logger

engine: AsyncEngine = create_async_engine(settings.POSTGRES_URL, echo=True)
async_session_maker: sessionmaker[AsyncSession] = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        logger.info("Database session created.")
        yield session