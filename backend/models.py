from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import datetime as dt

class ProductBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    my_price: float
    url: Optional[str] = None

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    competitor_prices: List["CompetitorPrice"] = Relationship(back_populates="product")
    recommendations: List["Recommendation"] = Relationship(back_populates="product")

class CompetitorPriceBase(SQLModel):
    competitor_name: str
    price: float
    discount_price: Optional[float] = None
    in_stock: bool = True
    url: str
    timestamp: datetime = Field(default_factory=dt.datetime.utcnow)

class CompetitorPrice(CompetitorPriceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="competitor_prices")

class RecommendationBase(SQLModel):
    action: str = Field(description="Action to take: 'raise', 'lower', or 'keep'")
    suggested_price: float
    reason: str
    timestamp: datetime = Field(default_factory=dt.datetime.utcnow)

class Recommendation(RecommendationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    product: Product = Relationship(back_populates="recommendations")
