from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from backend.app.db.database import engine, Base, AsyncSessionLocal
from backend.app.routers import auth, products, carts, purchase, browsing
from sqlalchemy.sql import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Running DB migrations and connecting to Redis...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    #await redis_cache.connect()
    yield
    print("Shutting down: Closing DB and Redis connections...")
    #await redis_cache.disconnect()
    await engine.dispose()

def rate_limit_exceeded_handler(request: Request, exc: Union[Exception, RateLimitExceeded]):
    return  JSONResponse(status_code=429, content={"error": "Too many request. Try again later."})

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(carts.router)
app.include_router(purchase.router)
app.include_router(browsing.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Smart Shopping Assistance API!"}

@app.get('/test-db')
async def test_db():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status":"Database Connected"}
    except Exception as e:
        return {"status":"Database Connection Failed","error":str(e)}
    finally:
        await session.close()