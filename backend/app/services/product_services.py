from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from backend.app.models import models
from backend.app.db.database import get_db
from backend.app.db.schemas import ProductSummary, ProductDetail, TokenData
from backend.app.services.user_services import UserService
from backend.app.auth.oauth2 import get_current_user_optional

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
    async def get_product(product_id: int, db: AsyncSession = Depends(get_db),
                          current_user: Optional[TokenData] = Depends(get_current_user_optional)) -> ProductDetail:

        user_id = current_user.id if current_user else None

        query = select(models.Product).where(models.Product.id == product_id)
        result = await db.execute(query)
        product = result.scalars().first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if current_user:
            await UserService.log_product_view(user_id, product_id, db)
        
        return product