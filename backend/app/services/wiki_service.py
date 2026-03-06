"""百科服务。"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.wiki import WikiEntry


class WikiService:
    def __init__(self, db: Session):
        self.db = db

    def list_entries(self, *, keyword: Optional[str], category: Optional[str], page: int, page_size: int) -> Tuple[list[WikiEntry], int]:
        q = self.db.query(WikiEntry).filter(WikiEntry.status == "approved")
        if keyword:
            like = f"%{keyword}%"
            q = q.filter(or_(WikiEntry.title.like(like), WikiEntry.content.like(like)))
        if category:
            q = q.filter(WikiEntry.category == category)
        total = q.count()
        items = (
            q.order_by(WikiEntry.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_entry(self, entry_id: int) -> Optional[WikiEntry]:
        return self.db.query(WikiEntry).filter(WikiEntry.id == entry_id, WikiEntry.status == "approved").first()
