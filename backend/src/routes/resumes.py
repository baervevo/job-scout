from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil, os

from src.models.resume.resume import Resume
from src.db.schemas.resume import Resume as ResumeSchema
from src.db.schemas.user import User
from src.db.session import get_db

from src.processing.resume_processing_queue import ResumeProcessingQueue, get_resume_processing_queue

from src.utils.pdf import extract_text_from_pdf

from config import settings
from src.utils.logger import logger

router = APIRouter()
UPLOAD_DIR = settings.RESUME_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{user_id}/resumes", response_model=None)
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    resume_processing_queue: ResumeProcessingQueue = Depends(get_resume_processing_queue)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        saved_path = os.path.join(UPLOAD_DIR, f"user_{user_id}_{file.filename}")
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if saved_path.endswith('.pdf'):
            content = extract_text_from_pdf(saved_path)
        else:
            content = None
        resume = Resume(
            user_id=user_id,
            file_name=file.filename,
            file_path=saved_path,
            content=content
        )
        resume_db = ResumeSchema(
            user_id=user_id,
            file_name=file.filename,
            file_path=saved_path,
        )
        db.add(resume_db)
        await db.commit()
        await db.refresh(resume_db)
        resume.id = resume_db.id
        logger.info(resume)
        resume_processing_queue.enqueue(resume)
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
    return {"success": True, "message": "Resume uploaded successfully"}


@router.get("/{user_id}/resumes", response_model=List[Resume])
async def get_user_resumes(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResumeSchema).filter(ResumeSchema.user_id == user_id))
    resumes = result.scalars().all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for this user")
    return [
        Resume(
            id=resume.id,
            user_id=resume.user_id,
            file_name=resume.file_name,
            file_path=resume.file_path,
            content=None
        )
        for resume in resumes
    ]


@router.get("/resumes/{resume_id}/file")
async def get_resume_file(
    resume_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResumeSchema).filter(ResumeSchema.id == resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        resume.file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(resume.file_path)
    )
