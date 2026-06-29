"""文化分享模型：视频推荐 & 每周荐读。"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from app.db.base import Base


class VideoRecommendation(Base):
    """戏曲视频推荐条目（外链）。"""

    __tablename__ = "video_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    platform = Column(String(30), nullable=False, default="bilibili")  # bilibili / youtube / other
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    opera_genre = Column(String(100), nullable=True)
    duration_display = Column(String(20), nullable=True)   # e.g. "45:32"
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WeeklyDigest(Base):
    """每周戏曲荐读。"""

    __tablename__ = "weekly_digests"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)          # ISO week (1-53)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    items_json = Column(Text, nullable=False, default="[]")  # JSON array of {title, url, type, desc}
    published_at = Column(DateTime, nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
