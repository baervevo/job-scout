from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

from src.models.user import User

router = APIRouter()

@router.post("/login")
async def login(
    username: str, 
    password: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
    
@router.post("/register")
async def register(
    username: str, 
    password: str,
    db: AsyncSession = Depends(get_db),
):
    # Placeholder for actual registration logic
    if username and password:
        return {"message": "Registration successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid input")