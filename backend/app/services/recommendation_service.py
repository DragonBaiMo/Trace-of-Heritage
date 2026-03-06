"""个性化推荐服务。"""
from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models.post import Reaction
from app.models.resource import Resource


class RecommendationService:
    """基于用户互动历史的轻量推荐实现。"""

    def __init__(self, db: Session):
        self.db = db

    def recommend_resources(self, user_id: int, limit: int = 10) -> List[Resource]:
        """
        返回推荐资源列表。

        算法：统计用户对资源的点赞/收藏历史，提取流派与标签，按匹配度评分排序。
        """

        liked_resource_ids = [
            item.target_id
            for item in self.db.query(Reaction)
            .filter(
                Reaction.user_id == user_id,
                Reaction.target_type == "resource",
                Reaction.reaction_type.in_(["like", "favorite"]),
            )
            .all()
        ]

        preferred_genres = set()
        preferred_tags = set()
        if liked_resource_ids:
            for item in (
                self.db.query(Resource)
                .filter(Resource.id.in_(liked_resource_ids))
                .all()
            ):
                if item.genre:
                    preferred_genres.add(item.genre)
                preferred_tags.update(item.tags or [])

        candidates: list[Resource] = (
            self.db.query(Resource)
            .filter(Resource.status == "approved")
            .order_by(Resource.created_at.desc())
            .limit(200)
            .all()
        )

        # 评分：同流派加 3，每个重叠标签加 1
        scored: list[tuple[int, Resource]] = []
        for res in candidates:
            if res.id in liked_resource_ids:
                continue
            score = 0
            if preferred_genres and res.genre in preferred_genres:
                score += 3
            if preferred_tags:
                overlap = preferred_tags.intersection(set(res.tags or []))
                score += len(overlap)
            if score > 0 or not liked_resource_ids:
                scored.append((score, res))

        scored.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
        top_recommended = [item[1] for item in scored[:limit]]

        if top_recommended:
            return top_recommended
        # 无行为或无匹配时，返回最新的内容作为兜底
        return candidates[:limit]
