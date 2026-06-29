"""文化分享服务。"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.cultural import VideoRecommendation, WeeklyDigest


class CulturalService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- 视频推荐 ----------

    def list_videos(
        self,
        genre: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[VideoRecommendation], int]:
        q = self.db.query(VideoRecommendation).filter(VideoRecommendation.is_active == True)
        if genre:
            q = q.filter(VideoRecommendation.opera_genre == genre)
        total = q.count()
        items = (
            q.order_by(VideoRecommendation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    # ---------- 每周荐读 ----------

    def list_digests(
        self, page: int = 1, page_size: int = 10
    ) -> Tuple[List[WeeklyDigest], int]:
        q = (
            self.db.query(WeeklyDigest)
            .filter(WeeklyDigest.is_published == True)
            .order_by(WeeklyDigest.year.desc(), WeeklyDigest.week_number.desc())
        )
        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_latest_digest(self) -> Optional[WeeklyDigest]:
        return (
            self.db.query(WeeklyDigest)
            .filter(WeeklyDigest.is_published == True)
            .order_by(WeeklyDigest.year.desc(), WeeklyDigest.week_number.desc())
            .first()
        )
