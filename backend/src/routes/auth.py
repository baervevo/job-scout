from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.user import User as UserSchema
from src.db.session import get_db
from src.utils.logger import logger
from src.utils.password import hash_password, verify_password

router = APIRouter()


@router.post("/login")
async def login(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            select(UserSchema).where(UserSchema.login == login)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        request.session["user_id"] = user.id
        logger.info(f"User {login} logged in successfully")
        return {"success": True, "user_id": user.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {login}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register")
async def register(
        login: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_db),
):
    if not login or not password:
        raise HTTPException(status_code=400, detail="Login and password are required")
    try:
        logger.info(f"Attempting to register user: {login}")
        existing_user_result = await db.execute(
            select(UserSchema).filter(UserSchema.login == login)
        )
        existing_user = existing_user_result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash the password before storing
        hashed_password = hash_password(password)
        new_user = UserSchema(login=login, password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"User {login} registered successfully with ID {new_user.id}")
        return {"success": True, "user_id": new_user.id}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error for user {login}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(request: Request):
    try:
        user_id = request.session.get("user_id")
        request.session.clear()
        logger.info(f"User {user_id} logged out successfully")
        return {"success": True}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
