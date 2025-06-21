from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import shutil, os

from src.db.schemas.resume import Resume
from src.db.schemas.user import User
from src.db.session import get_db

from src.processing.resume_processing_queue import ResumeProcessingQueue, get_resume_processing_queue

from config import settings

router = APIRouter()
UPLOAD_DIR = settings.RESUME_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/users/{user_id}/resumes")
def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    resume_processing_queue: ResumeProcessingQueue = Depends(get_resume_processing_queue)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        saved_path = os.path.join(UPLOAD_DIR, f"user_{user_id}_{file.filename}")
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resume = Resume(
            user_id=user_id,
            file_name=file.filename,
            file_path=saved_path,
        )
        db.add(resume)
        db.commit()
        resume_processing_queue.enqueue(resume)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")

    return {"success": True, "message": "Resume uploaded successfully"}
