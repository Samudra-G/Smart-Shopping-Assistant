from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.database import get_db
from backend.app.db.schemas import ProductSummary, ProductDetail
from backend.app.services.product_services import ProductService
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/v1/products", 
    tags=["Products"])

@router.get("/", response_model=list[ProductSummary])
@limiter.limit("20/minute")
async def get_products(request: Request, db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10):
    return await ProductService.get_products(db, page, limit)

@router.get("/search", response_model=list[ProductSummary])
@limiter.limit("10/minute")
async def search_products(request: Request, q: str = Query(..., min_length=2), limit: int = 10,
                            db: AsyncSession = Depends(get_db)):
    return await ProductService.search_products(q, limit, db)

@router.get("/{product_id}", response_model=ProductDetail)
@limiter.limit("10/minute")
async def get_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    return await ProductService.get_product(product_id, db)
