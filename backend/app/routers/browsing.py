from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request
from backend.app.models import models
from backend.app.db.database import get_db
from backend.app.auth.oauth2 import get_current_user
from backend.app.db.schemas import BrowsingHistoryItem

router = APIRouter(
    prefix="/v1/browsing",
    tags=["Browsing History"]
)

@router.get("/history", response_model=list[BrowsingHistoryItem])
async def get_browsing_history(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    query = (   
        select(models.BrowsingHistory)
        .options(selectinload(models.BrowsingHistory.product))
        .where(models.BrowsingHistory.user_id == current_user.id)
        .order_by(models.BrowsingHistory.viewed_at.desc())
        .limit(20)
    )
    result = await db.execute(query)
    history = result.scalars().all()
    if not history:
        raise HTTPException(status_code=404, detail="No browsing history found")
    
    return history