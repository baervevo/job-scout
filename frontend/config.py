import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

import logging

# Load environment variables from .env file if it exists
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

print(f"Loading frontend environment variables from {env_path}")

class Settings(BaseSettings):
    # Frontend application settings
    FRONTEND_HOST: str = Field("127.0.0.1", env='FRONTEND_HOST')
    FRONTEND_PORT: int = Field(8000, env='FRONTEND_PORT')
    
    # Backend API configuration
    BACKEND_HOST: str = Field("127.0.0.1", env='BACKEND_HOST')
    BACKEND_PORT: int = Field(8080, env='BACKEND_PORT')
    BACKEND_PROTOCOL: str = Field("http", env='BACKEND_PROTOCOL')
    
    # Logging configuration
    LOGGING_LEVEL: int = Field(logging.INFO, env='LOGGING_LEVEL')
    LOGGING_FORMAT: str = Field(
        "%(name)s @ %(asctime)s [%(levelname)s]: %(message)s", 
        env='LOGGING_FORMAT'
    )
    
    # Development settings
    DEBUG: bool = Field(False, env='DEBUG')
    
    @property
    def API_URL(self) -> str:
        """Construct the full API URL"""
        return f"{self.BACKEND_PROTOCOL}://{self.BACKEND_HOST}:{self.BACKEND_PORT}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()