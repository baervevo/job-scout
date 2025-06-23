from fastapi import FastAPI
from src.app import app

from config import settings

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
