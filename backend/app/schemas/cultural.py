"""文化分享 schema。"""
from datetime import datetime
from typing import Any, List, Optional
import json
from pydantic import BaseModel, Field, validator


class VideoRecommendationRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    platform: str
    url: str
    thumbnail_url: Optional[str]
    opera_genre: Optional[str]
    duration_display: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class WeeklyDigestItemRead(BaseModel):
    title: str
    url: str
    type: str = "article"   # article / video
    desc: Optional[str] = None


class WeeklyDigestRead(BaseModel):
    id: int
    year: int
    week_number: int
    title: str
    summary: Optional[str]
    items: List[WeeklyDigestItemRead] = Field(default_factory=list)
    published_at: Optional[datetime]
    is_published: bool
    created_at: datetime

    @classmethod
    def from_orm(cls, obj: Any) -> "WeeklyDigestRead":  # type: ignore[override]
        raw = json.loads(obj.items_json or "[]")
        items = [WeeklyDigestItemRead(**i) for i in raw]
        return cls(
            id=obj.id,
            year=obj.year,
            week_number=obj.week_number,
            title=obj.title,
            summary=obj.summary,
            items=items,
            published_at=obj.published_at,
            is_published=obj.is_published,
            created_at=obj.created_at,
        )

    class Config:
        orm_mode = True
