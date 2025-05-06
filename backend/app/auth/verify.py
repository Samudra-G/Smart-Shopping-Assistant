import asyncio
from passlib.context import CryptContext
from datetime import datetime, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)