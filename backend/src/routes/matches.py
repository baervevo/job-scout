from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload

from src.db.schemas.match import Match as MatchSchema
from src.db.schemas.resume import Resume as ResumeSchema
from src.db.schemas.listing import Listing as ListingSchema
from src.db.schemas.company import Company as CompanySchema
from src.db.session import get_db
from src.utils.logger import logger

router = APIRouter()

@router.get("/")
async def get_user_matches(
    request: Request,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
) -> List[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(
            select(MatchSchema, ResumeSchema, ListingSchema, CompanySchema)
            .join(ResumeSchema, MatchSchema.resume_id == ResumeSchema.id)
            .join(ListingSchema, MatchSchema.listing_id == ListingSchema.id)
            .join(CompanySchema, ListingSchema.company_id == CompanySchema.id)
            .filter(ResumeSchema.user_id == user_id)
            .order_by(MatchSchema.cosine_similarity.desc())
            .limit(limit)
            .offset(offset)
        )
        
        matches_data = result.all()
        return [
            {
                "id": match.id,
                "resume_id": match.resume_id,
                "listing_id": match.listing_id,
                "missing_keywords": match.missing_keywords.split(",") if match.missing_keywords else [],
                "cosine_similarity": match.cosine_similarity,
                "summary": match.summary,
                "matched_at": match.matched_at.isoformat() if match.matched_at else None,
                "resume": {
                    "id": resume.id,
                    "file_name": resume.file_name
                },
                "listing": {
                    "id": listing.id,
                    "title": listing.title,
                    "company": company.name,
                    "location": listing.location,
                    "link": listing.link,
                    "salary_min": listing.salary_min,
                    "salary_max": listing.salary_max,
                    "currency": listing.currency
                }
            }
            for match, resume, listing, company in matches_data
        ]
    except Exception as e:
        logger.error(f"Error fetching matches for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch matches")

@router.get("/{match_id}")
async def get_match_details(
    match_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> dict:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        result = await db.execute(
            select(MatchSchema, ResumeSchema, ListingSchema, CompanySchema)
            .join(ResumeSchema, MatchSchema.resume_id == ResumeSchema.id)
            .join(ListingSchema, MatchSchema.listing_id == ListingSchema.id)
            .join(CompanySchema, ListingSchema.company_id == CompanySchema.id)
            .filter(
                and_(
                    MatchSchema.id == match_id,
                    ResumeSchema.user_id == user_id
                )
            )
        )
        
        match_data = result.first()
        if not match_data:
            raise HTTPException(status_code=404, detail="Match not found")
            
        match, resume, listing, company = match_data
        return {
            "id": match.id,
            "resume_id": match.resume_id,
            "listing_id": match.listing_id,
            "missing_keywords": match.missing_keywords.split(",") if match.missing_keywords else [],
            "cosine_similarity": match.cosine_similarity,
            "summary": match.summary,
            "matched_at": match.matched_at.isoformat() if match.matched_at else None,
            "resume": {
                "id": resume.id,
                "file_name": resume.file_name,
                "keywords": resume.keywords.split(",") if resume.keywords else []
            },
            "listing": {
                "id": listing.id,
                "title": listing.title,
                "company": company.name,
                "description": listing.description,
                "location": listing.location,
                "link": listing.link,
                "salary_min": listing.salary_min,
                "salary_max": listing.salary_max,
                "currency": listing.currency,
                "keywords": listing.keywords.split(",") if listing.keywords else []
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match {match_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch match details")