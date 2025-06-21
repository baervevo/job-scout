from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

from src.db.schemas.user import User as UserSchema

from src.utils.logger import logger

router = APIRouter()

@router.post("/login")
async def login(
    login: str = Form(...), 
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSchema).where(UserSchema.login == login)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.password == password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": "true"}
    
@router.post("/register")
async def register(
    login: str = Form(...), 
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Registering user: {login}")
    existing_user = await db.execute(
        select(UserSchema).filter(UserSchema.login == login)
    )
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="login already exists")
    new_user = UserSchema(login=login, password=password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"success": "true"}