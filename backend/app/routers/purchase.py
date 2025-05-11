from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy import insert, delete
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from backend.app.models import models
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.auth.oauth2 import get_current_user
from backend.app.db.database import get_db
from backend.app.db.schemas import PurchaseItemResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(
    prefix="/v1/purchase",
    tags=["Purchase"]
)

limiter = Limiter(key_func=get_remote_address)

@router.post("/checkout")
@limiter.limit("10/minute")
async def checkout(request: Request, db: AsyncSession = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    
    query = select(models.CartItem).filter(models.CartItem.user_id == current_user.id)
    result = await db.execute(query)
    items = result.scalars().all()

    if not items:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    purchase_entries = [
        {
            "user_id": item.user_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "purchased_at": datetime.now(timezone.utc)
        }
        for item in items
    ]
    stmt = insert(models.Purchase).values(purchase_entries)
    await db.execute(stmt)
    
    await db.execute(delete(models.CartItem).where(models.CartItem.user_id == current_user.id))
    await db.commit()

    return {"message": "Checkout successful!"}

@router.get("/history", response_model=list[PurchaseItemResponse])
@limiter.limit("10/minute")
async def purchase_history(request: Request, db: AsyncSession = Depends(get_db),
                            current_user: models.User = Depends(get_current_user)):
    query = select(models.Purchase).options(joinedload(models.Purchase.product)).where(models.Purchase.user_id == current_user.id)
    result = await db.execute(query)
    purchases = result.scalars().all()

    if not purchases:
        raise HTTPException(status_code=404, detail="No purchase history found")

    return purchases