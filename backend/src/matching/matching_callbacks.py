from src.models.match import Match
from src.utils.logger import logger

def log_match(match: Match) -> None:
    logger.info(f"Matched {match.resume_id} with {match.listing_id}, summary: {match.summary}")

async def commit_match_to_db(match: Match) -> None:
    from db.session import async_session_maker
    from db.schemas.match import Match as MatchSchema
    with async_session_maker() as db_session:
        data = match.model_dump(exclude_unset=True)
        row: MatchSchema = MatchSchema(**data)
        db_session.add(row)
        db_session.commit()