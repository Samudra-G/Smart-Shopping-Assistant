from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from backend.app.db import database, schemas
from backend.app.models.models import User
from backend.app.services.user_services import UserService
from backend.app.auth import verify, oauth2
from sqlalchemy.future import select
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"]
)

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                 db: AsyncSession = Depends(database.get_db)):
    try:
        query = select(User).where((or_(User.email == form_data.username, User.name == form_data.username)))
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        is_valid = await verify.verify_password(form_data.password, user.password) #type:ignore
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials. Try again.")
        
        access_token = oauth2.create_access_token(data={"user_id": user.user_id, "username": user.name})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Login failed.")
    

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    return await UserService.create_user(user, db)