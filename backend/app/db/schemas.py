from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Annotated
from datetime import datetime, date

#User schema
class UserCreate(BaseModel):
    name: Annotated[str, Field(..., alias="username", examples=["yourname"])]
    email: EmailStr = Field(..., examples=["yourname@example.com"])
    password: str = Field(..., min_length=8, examples=["your_strong_password_123"])

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

#Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None