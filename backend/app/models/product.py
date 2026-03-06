"""积分商城相关模型。"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    cover = Column(String(255), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    points_price = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")  # active/inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserPoint(Base):
    __tablename__ = "user_points"

    user_id = Column(Integer, primary_key=True, index=True)
    balance = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    points_cost = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="pending")  # pending/shipped/completed/canceled
    shipping_remark = Column(String(255), nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product")
