from backend.app.db.database  import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime, Date, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="regular")

    #relations
    purchases = relationship("Purchase", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, auto_increment=True)
    name = Column(String, index=True)
    category = Column(String)
    description = Column(String)
    price = Column(Float)
    final_price = Column(Float, nullable=True)
    brand = Column(String, nullable=True)
    discount = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    image_urls = Column(JSON, nullable=True)
    rating_stars = Column(Float, nullable=True)
    sizes = Column(JSON, nullable=True)
    colors = Column(JSON, nullable=True)
    seller = Column(String, nullable=True)
    top_reviews = Column(JSON, nullable=True)
    categories = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    #relations
    purchases = relationship("Purchase", back_populates="product")

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    purchased_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    #relations
    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")

#Optional
class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Float)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
