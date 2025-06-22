from datetime import datetime
from src.models.match import Match
from src.utils.logger import logger

def log_match(match: Match) -> None:
    logger.info(f"Matched resume {match.resume_id} with listing {match.listing_id}, similarity: {match.cosine_similarity:.3f}")

async def commit_match_to_db(match: Match) -> None:
    try:
        from src.db.session import async_session_maker
        from src.db.schemas.match import Match as MatchSchema
        
        async with async_session_maker() as db_session:
            missing_keywords_str = ",".join(match.missing_keywords) if match.missing_keywords else ""
            match_data = {
                "resume_id": int(match.resume_id) if match.resume_id else None,
                "listing_id": int(match.listing_id) if match.listing_id else None,
                "missing_keywords": missing_keywords_str,
                "cosine_similarity": match.cosine_similarity or 0.0,
                "summary": match.summary or "",
                "matched_at": datetime.utcnow()
            }
            if not match_data["resume_id"] or not match_data["listing_id"]:
                logger.error(f"Invalid match data: missing resume_id or listing_id")
                return
            row = MatchSchema(**match_data)
            db_session.add(row)
            await db_session.commit()
            await db_session.refresh(row)
            logger.info(f"Successfully committed match {row.id} to database")
                
    except Exception as e:
        logger.error(f"Failed to commit match to database: {str(e)}")