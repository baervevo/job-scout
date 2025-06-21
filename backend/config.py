import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

import logging

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

print(f"Loading environment variables from {env_path}")

class Settings(BaseSettings):
    APP_HOST: str = Field(..., env='APP_HOST')
    APP_PORT: int = Field(..., env='APP_PORT')

    # Database configuration
    POSTGRES_USER: str = Field(..., env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(..., env='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field(..., env='POSTGRES_DB')
    POSTGRES_HOST: str = Field(..., env='POSTGRES_HOST')
    POSTGRES_PORT: str = Field(..., env='POSTGRES_PORT')

    RESUME_DIR: str = Field(..., env='RESUME_DIR')

    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    JOOBLE_API_KEY: str = Field(..., env='JOOBLE_API_KEY')
    JOOBLE_HOST: str = "https://jooble.org"
    JOOBLE_MAX_RESULTS: int = Field(2, env='JOOBLE_MAX_RESULTS')

    LOGGING_LEVEL: int = logging.DEBUG
    LOGGING_FORMAT: str = "%(name)s @ %(asctime)s [%(levelname)s]: %(message)s"

    MATCHING_COSINE_THRESHOLD: float = Field(0.5, env='MATCHING_COSINE_THRESHOLD')
    
settings = Settings()