"""百科模型。"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class WikiEntry(Base):
    """戏曲百科词条。"""

    __tablename__ = "wiki_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="approved")  # approved/pending/rejected
    author_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
