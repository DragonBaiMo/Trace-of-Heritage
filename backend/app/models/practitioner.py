"""从业者认证申请模型。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PractitionerApplication(Base):
    """从业者认证申请记录。"""

    __tablename__ = "practitioner_applications"

    id = Column(Integer, primary_key=True, index=True)
    realname = Column(String(100), nullable=False)
    title = Column(String(120), nullable=False)
    bio = Column(String(1000), nullable=True)
    attachment = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending/approved/rejected

    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_note = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    applicant = relationship("User", foreign_keys=[applicant_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
