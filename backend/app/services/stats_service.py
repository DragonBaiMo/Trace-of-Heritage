"""统计看板数据服务。"""
from datetime import datetime, timedelta

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityEnrollment
from app.models.post import Post
from app.models.resource import Resource
from app.schemas.stats import DashboardStats


class StatsService:
    """汇总统计图表数据。"""

    def __init__(self, db: Session):
        self.db = db

    def load_dashboard(self) -> DashboardStats:
        """汇总看板所需的全部数据。"""

        return DashboardStats(
            resource_trend=self._resource_trend(),
            topic_hot=self._topic_hot(),
            region_distribution=self._region_distribution(),
            activity_participants=self._activity_participants(),
        )

    def _resource_trend(self) -> list[dict[str, str | int]]:
        """统计近 30 天资源新增量。"""

        since = datetime.utcnow().date() - timedelta(days=29)
        rows = (
            self.db.query(
                func.date(Resource.created_at).label("day"),
                func.count(Resource.id).label("count"),
            )
            .filter(Resource.created_at >= since)
            .group_by(func.date(Resource.created_at))
            .order_by(func.date(Resource.created_at))
            .all()
        )
        mapping = {}
        for row in rows:
            day_value = row.day
            if isinstance(day_value, str):
                day_value = datetime.fromisoformat(day_value).date()
            mapping[day_value] = int(row.count or 0)
        result = []
        for index in range(30):
            day = since + timedelta(days=index)
            result.append({"day": day, "count": mapping.get(day, 0)})
        return result

    def _topic_hot(self) -> list[dict[str, str | int]]:
        """统计热门话题。"""

        rows = (
            self.db.query(Post.topic, func.count(Post.id).label("count"))
            .filter(Post.status == "approved", Post.topic.isnot(None))
            .group_by(Post.topic)
            .order_by(func.count(Post.id).desc())
            .limit(10)
            .all()
        )
        return [
            {"name": row.topic, "value": int(row.count or 0)}
            for row in rows
        ]

    def _region_distribution(self) -> list[dict[str, str | int]]:
        """统计资源地区分布。"""

        rows = (
            self.db.query(Resource.region_code, func.count(Resource.id).label("count"))
            .filter(Resource.status == "approved", Resource.region_code.isnot(None))
            .group_by(Resource.region_code)
            .order_by(func.count(Resource.id).desc())
            .all()
        )
        return [
            {"name": row.region_code or "未知", "value": int(row.count or 0)}
            for row in rows
        ]

    def _activity_participants(self) -> list[dict[str, str | int]]:
        """统计活动报名情况。"""

        rows = (
            self.db.query(
                Activity.title,
                func.count(ActivityEnrollment.id).label("enrolled"),
                func.sum(case((ActivityEnrollment.status == "checked_in", 1), else_=0)).label("checked_in"),
            )
            .outerjoin(ActivityEnrollment, ActivityEnrollment.activity_id == Activity.id)
            .filter(Activity.status == "approved")
            .group_by(Activity.id)
            .order_by(Activity.start_time.desc())
            .all()
        )
        return [
            {
                "title": row.title,
                "enrolled": int(row.enrolled or 0),
                "checked_in": int(row.checked_in or 0),
            }
            for row in rows
        ]
