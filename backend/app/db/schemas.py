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

#Product schema
class ProductBase(BaseModel):
    name: str
    category: str
    description: str
    price: float
    final_price: Optional[float] = None
    brand: Optional[str] = None
    discount: Optional[str] = None
    currency: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    rating_stars: Optional[float] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    seller: Optional[str] = None
    top_reviews: Optional[dict[str,dict]] = None
    categories: Optional[List[str]] = None

class ProductSummary(BaseModel):
    id: int
    name: str
    category: str
    price: float
    final_price: Optional[float] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    rating_stars: Optional[float] = None

    class Config:
        from_attributes = True

class ProductDetail(ProductBase):
    id: int

    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: Optional[int] = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    added_at: datetime

    class Config:
        from_attributes = True

class CartItemUpdate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class PurchaseItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    purchased_at: datetime
    product: Optional[ProductSummary]

    class Config:
        from_attributes = True

class BrowsingHistoryItem(BaseModel):
    id: int
    product_id: int
    viewed_at: datetime
    product: Optional[ProductSummary]

    class Config:
        from_attributes = True

#Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None