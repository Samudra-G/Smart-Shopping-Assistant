from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy import insert, delete
from sqlalchemy.future import select
from backend.app.models import models
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.auth.oauth2 import get_current_user
from backend.app.db.database import get_db
from backend.app.db.schemas import CartItemCreate, CartItemResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(
    prefix="/v1/cart",
    tags=["Cart"]
)

limiter = Limiter(key_func=get_remote_address)

@router.post("/add")
@limiter.limit("10/minute")
async def add_to_cart(request: Request, item: CartItemCreate, db: AsyncSession = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    
    cart_entry = insert(models.CartItem).values(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity,
        added_at=datetime.now(timezone.utc)
    )
    await db.execute(cart_entry)
    await db.commit()
    return {"message": "Item added to cart!"}

@router.get("/items", response_model=list[CartItemResponse])
@limiter.limit("10/minute")
async def get_cart_items(request: Request, db: AsyncSession = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    query = select(models.CartItem).filter(models.CartItem.user_id == current_user.id)
    result = await db.execute(query)
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=404, detail="No items found in cart")

    return cart_items

@router.delete("/remove/{item_id}")
@limiter.limit("10/minute")
async def remove_from_cart(request: Request, item_id: int, db: AsyncSession = Depends(get_db),
                            current_user: models.User = Depends(get_current_user)):

        if not item_id:
            raise HTTPException(status_code=400, detail="Product ID is required")
        
        query = select(models.CartItem).where(
        models.CartItem.product_id == item_id,
        models.CartItem.user_id == current_user.id
        )
        result = await db.execute(query)
        item = result.scalars().first()

        if not item:
            raise HTTPException(status_code=404, detail="Item does not exist in your cart.")
        
        stmt = delete(models.CartItem).where(models.CartItem.product_id == item_id)
        await db.execute(stmt)
        await db.commit()

        return {"message": "Item removed from your cart."}
    
    