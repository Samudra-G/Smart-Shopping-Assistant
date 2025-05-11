import os
from dotenv import load_dotenv
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from typing import cast, Optional
from backend.app.db.schemas import TokenData
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
SECRET_KEY = cast(str, os.getenv("SECRET_KEY"))
ALGORITHM = cast(str, os.getenv("ALGORITHM"))

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set")
if ALGORITHM is None:
    raise ValueError("ALGORITHM environment variable is not set")

ACCESS_TOKEN_EXPIRATION_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRATION_MINUTES", 30))
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: Optional[str] = request.headers.get("Authorization")
        if not authorization:
            return None
        return await super().__call__(request)


oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES)
    to_encode.update({
        "exp": expire,
        "user_id": data.get("user_id"),
        "username": data.get("username")
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: Optional[int] = payload.get("user_id")
        name: Optional[str] = payload.get("username")
    
        token_data = TokenData(id= user_id, name= name)

        return token_data
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials", 
                                         headers={"WWW-Authenticate":"Bearer"})
    
    return verify_access_token(token, credentials_exception)

def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[TokenData]:

    if token is None:
        return None
    
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials", 
                                         headers={"WWW-Authenticate":"Bearer"})

    try:
        return verify_access_token(token, credentials_exception)
    except HTTPException:
        return None