"""活动相关服务。"""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.localization.messages import MESSAGES
from app.models.activity import Activity, ActivityEnrollment
from app.schemas.activity import ActivityCreate
from app.utils.exceptions import BusinessException


class ActivityService:
    """封装活动领域逻辑。"""

    def __init__(self, db: Session):
        self.db = db

    def create_activity(self, payload: ActivityCreate, creator_id: int) -> Activity:
        """创建活动。"""

        activity = Activity(
            title=payload.title,
            description=payload.description,
            location=payload.location,
            start_time=payload.start_time,
            end_time=payload.end_time,
            quota=payload.quota,
            status="pending" if payload.submit_for_review else "draft",
            creator_id=creator_id,
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def list_activities(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_role: str,
        current_user_id: int,
    ) -> tuple[list[Activity], int]:
        """分页查询活动。"""

        query = self.db.query(Activity)
        if status:
            query = query.filter(Activity.status == status)
        if current_user_role != "admin":
            query = query.filter((Activity.status == "approved") | (Activity.creator_id == current_user_id))
        total = query.count()
        items = (
            query.order_by(Activity.start_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def review_activity(self, activity: Activity, decision: str, review_note: Optional[str], reviewer_id: int) -> Activity:
        """审核活动。"""

        if activity.status not in {"pending", "draft"}:
            raise BusinessException(MESSAGES["resource_invalid_state"])
        if decision == "reject" and (not review_note or len(review_note.strip()) < 5):
            raise BusinessException(MESSAGES["review_note_required"])
        activity.status = "approved" if decision == "approve" else "rejected"
        activity.review_note = review_note
        activity.reviewer_id = reviewer_id
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def enroll(self, activity: Activity, user_id: int) -> ActivityEnrollment:
        """报名活动。"""

        if activity.status != "approved" or activity.end_time <= datetime.utcnow():
            raise BusinessException(MESSAGES["activity_closed"], code=41001)
        enrolled_count = (
            self.db.query(func.count(ActivityEnrollment.id))
            .filter(ActivityEnrollment.activity_id == activity.id, ActivityEnrollment.status != "cancelled")
            .scalar()
            or 0
        )
        if enrolled_count >= activity.quota:
            raise BusinessException(MESSAGES["activity_closed"], code=41001)
        existing = (
            self.db.query(ActivityEnrollment)
            .filter(ActivityEnrollment.activity_id == activity.id, ActivityEnrollment.user_id == user_id)
            .first()
        )
        if existing:
            return existing
        enrollment = ActivityEnrollment(activity_id=activity.id, user_id=user_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def list_user_enrolled_activities(
        self,
        *,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Activity], int]:
        """分页返回用户已报名的活动列表（不含已取消）。"""

        q = (
            self.db.query(Activity)
            .join(ActivityEnrollment, ActivityEnrollment.activity_id == Activity.id)
            .filter(ActivityEnrollment.user_id == user_id, ActivityEnrollment.status != "cancelled")
        )
        total = q.count()
        items = (
            q.order_by(Activity.start_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def check_in(self, activity: Activity, user_id: int) -> ActivityEnrollment:
        """签到。"""

        enrollment = (
            self.db.query(ActivityEnrollment)
            .filter(
                ActivityEnrollment.activity_id == activity.id,
                ActivityEnrollment.user_id == user_id,
                ActivityEnrollment.status == "applied",
            )
            .first()
        )
        if not enrollment:
            raise BusinessException(MESSAGES["enroll_not_found"])
        enrollment.status = "checked_in"
        enrollment.checked_in_at = datetime.utcnow()
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def stats(self) -> list[dict[str, int | str]]:
        """统计活动报名与签到情况。"""

        rows = (
            self.db.query(
                Activity.title,
                func.count(ActivityEnrollment.id).label("enrolled"),
                func.sum(case((ActivityEnrollment.status == "checked_in", 1), else_=0)).label("checked_in"),
            )
            .outerjoin(ActivityEnrollment, ActivityEnrollment.activity_id == Activity.id)
            .filter(Activity.status == "approved")
            .group_by(Activity.id)
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
