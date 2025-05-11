from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, Depends
from backend.app.models.models import User
from backend.app.db.schemas import UserCreate
from backend.app.auth.verify import hash_password
from backend.app.auth.oauth2 import get_current_user
from backend.app.models import models
from typing import Optional

class UserService:

    @staticmethod
    async def create_user(user: UserCreate, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = await hash_password(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        new_user = User(**user_data)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user
    
    @staticmethod
    async def get_me(current_username: str, db:AsyncSession):
        result = await db.execute(select(User).where(User.name == current_username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    @staticmethod
    async def get_user(user_id: int, db: AsyncSession):
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        return user
    
    @staticmethod
    async def log_product_view(user_id: Optional[int], product_id: int, db: AsyncSession):
        
        if user_id is not None:
            entry = models.BrowsingHistory(user_id=user_id, product_id=product_id)
            db.add(entry)
            await db.commit()