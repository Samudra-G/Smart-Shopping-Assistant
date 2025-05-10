from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from backend.app.models import models
from backend.app.db.database import get_db
from backend.app.db.schemas import ProductSummary, ProductDetail

class ProductService:
    @staticmethod
    async def get_products(db: AsyncSession, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        query = select(models.Product).offset(offset).limit(limit)
        result = await db.execute(query)
        products = result.scalars().all()
        
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        
        return products

    @staticmethod
    async def search_products(q: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
        if len(q) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters long")
        
        query = select(models.Product).where(
            or_(
                models.Product.name.ilike(f"%{q}%"),
                models.Product.brand.ilike(f"%{q}%"),
                models.Product.category.ilike(f"%{q}%")
            )
        ).limit(limit)

        result = await db.execute(query)
        products = result.scalars().all()
            
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        
        return products

    @staticmethod
    async def get_product(product_id: int, db: AsyncSession) -> ProductDetail:
        query = select(models.Product).where(models.Product.id == product_id)
        result = await db.execute(query)
        product = result.scalars().first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product