"""系统公告模型。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


class Notice(Base):
    """管理员发布的系统公告。"""

    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    content = Column(Text, nullable=False)
    audience = Column(String(20), nullable=False, default="all")
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
