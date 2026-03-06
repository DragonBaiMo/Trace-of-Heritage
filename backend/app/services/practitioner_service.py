"""从业者认证服务层。"""
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.practitioner import PractitionerApplication
from app.models.user import User
from app.schemas.practitioner import PractitionerApply
from app.localization.messages import MESSAGES
from app.utils.exceptions import BusinessException


class PractitionerService:
    """封装从业者认证申请与审核逻辑。"""

    def __init__(self, db: Session):
        self.db = db

    def apply(self, applicant_id: int, payload: PractitionerApply) -> PractitionerApplication:
        """提交从业者认证申请。若存在未完结申请则阻止重复提交。"""
        exists = (
            self.db.query(PractitionerApplication)
            .filter(
                PractitionerApplication.applicant_id == applicant_id,
                PractitionerApplication.status.in_(["pending"]) ,
            )
            .first()
        )
        if exists:
            raise BusinessException("已存在待处理的认证申请，请耐心等待审核结果")
        app = PractitionerApplication(
            realname=payload.realname,
            title=payload.title,
            bio=payload.bio,
            attachment=payload.attachment,
            applicant_id=applicant_id,
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app

    def list_applications(self, status: str | None = None) -> Iterable[PractitionerApplication]:
        """列出所有认证申请，按时间倒序，可按状态过滤。"""
        query = self.db.query(PractitionerApplication).order_by(PractitionerApplication.created_at.desc())
        if status:
            query = query.filter(PractitionerApplication.status == status)
        return query.all()

    def review(self, application: PractitionerApplication, decision: str, review_note: str | None, reviewer_id: int) -> PractitionerApplication:
        """审核申请。通过则将申请人角色置为 practitioner。"""
        if decision not in {"approve", "reject"}:
            raise BusinessException("非法的审核决策")
        if application.status != "pending":
            raise BusinessException(MESSAGES["pract_already_reviewed"])
        if decision == "reject" and (not review_note or not review_note.strip()):
            raise BusinessException(MESSAGES["review_note_required"])
        application.status = "approved" if decision == "approve" else "rejected"
        application.review_note = review_note
        application.reviewer_id = reviewer_id
        # 审核通过，升级角色
        if decision == "approve":
            user = self.db.query(User).filter(User.id == application.applicant_id).first()
            if user and user.role == "user":
                user.role = "practitioner"
                self.db.add(user)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
