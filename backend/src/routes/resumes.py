from typing import List
import os
import shutil
import asyncio
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.resume.resume import Resume
from src.db.schemas.resume import Resume as ResumeSchema
from src.db.schemas.user import User
from src.db.session import get_db

from src.processing.resume_processing_queue import ResumeProcessingQueue, get_resume_processing_queue
from src.utils.pdf import extract_text_from_pdf

from config import settings
from src.utils.logger import logger

router = APIRouter()
UPLOAD_DIR = Path(settings.RESUME_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if hasattr(file, 'size') and file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

async def save_file_async(file: UploadFile, file_path: Path) -> None:
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save file")

async def process_resume_content(file_path: Path) -> str:
    try:
        if file_path.suffix.lower() == '.pdf':
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, extract_text_from_pdf, str(file_path))
            return content
        else:
            return ""
    except Exception as e:
        logger.error(f"Error extracting content from {file_path}: {str(e)}")
        return ""

@router.post("/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    resume_processing_queue: ResumeProcessingQueue = Depends(get_resume_processing_queue)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Database error checking user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    
    validate_file(file)
    file_path = None
    try:
        file_ext = Path(file.filename).suffix
        unique_filename = f"user_{user_id}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename
        await save_file_async(file, file_path)
        logger.info(f"File saved to {file_path}")
        content = await process_resume_content(file_path)
        
        resume_db = ResumeSchema(
            user_id=user_id,
            file_name=file.filename,
            file_path=str(file_path),
        )
        db.add(resume_db)
        await db.commit()
        await db.refresh(resume_db)
        
        resume = Resume(
            id=str(resume_db.id),
            user_id=user_id,
            file_name=file.filename,
            file_path=str(file_path),
            content=content
        )
        resume_processing_queue.enqueue(resume)
        logger.info(f"Resume {resume.id} queued for processing")
        return {
            "success": True, 
            "message": "Resume uploaded successfully",
            "resume_id": resume_db.id,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to upload resume for user {user_id}: {str(e)}")
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file {file_path}: {cleanup_error}")
        
        raise HTTPException(status_code=500, detail="Upload failed")

@router.get("/")
async def get_user_resumes(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(
            select(ResumeSchema).filter(ResumeSchema.user_id == user_id)
        )
        resumes = result.scalars().all()
        return [
            {
                "id": resume.id,
                "user_id": resume.user_id,
                "file_name": resume.file_name,
                "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
                "keywords": resume.keywords.split(",") if resume.keywords else [],
                "last_evaluated_at": resume.last_evaluated_at.isoformat() if resume.last_evaluated_at else None
            }
            for resume in resumes
        ]
    except Exception as e:
        logger.error(f"Error fetching resumes for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch resumes")

@router.get("/{resume_id}/file")
async def get_resume_file(
    resume_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(
            select(ResumeSchema).filter(
                ResumeSchema.id == resume_id,
                ResumeSchema.user_id == user_id
            )
        )
        resume = result.scalars().first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        file_path = Path(resume.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        return FileResponse(
            path=str(file_path),
            media_type="application/octet-stream",
            filename=resume.file_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file for resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve file")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(
            select(ResumeSchema).filter(
                ResumeSchema.id == resume_id,
                ResumeSchema.user_id == user_id
            )
        )
        resume = result.scalars().first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        file_path = Path(resume.file_path)
        if file_path.exists():
            file_path.unlink()
        await db.delete(resume)
        await db.commit()
        logger.info(f"Resume {resume_id} deleted successfully")
        return {"success": True, "message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete resume")
