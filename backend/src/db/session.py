from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator

from config import settings

engine: AsyncEngine = create_async_engine(settings.POSTGRES_URL, echo=True)
AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[Session, None, None]:
    async with AsyncSessionLocal() as session:
        yield session
