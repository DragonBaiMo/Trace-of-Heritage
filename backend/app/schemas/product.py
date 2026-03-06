"""积分商城 schema。"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductRead(BaseModel):
    id: int
    title: str
    cover: Optional[str]
    price: Optional[float]
    points_price: int
    stock: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    title: str
    cover: Optional[str] = None
    price: Optional[float] = None
    points_price: int
    stock: int = 0
    status: str = "active"

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    cover: Optional[str] = None
    price: Optional[float] = None
    points_price: Optional[int] = None
    stock: Optional[int] = None
    status: Optional[str] = None


class OrderCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(1, ge=1, le=99)


class PointsRead(BaseModel):
    balance: int


class OrderRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    points_cost: int
    status: str
    shipping_remark: Optional[str]
    shipped_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


class OrderShipRequest(BaseModel):
    """管理员发货请求体。"""

    remark: Optional[str] = Field(None, max_length=255, description="发货备注/物流单号")
