"""活动域模型，覆盖活动与报名。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Activity(Base):
    """线下或线上活动。"""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    quota = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", foreign_keys=[creator_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    enrollments = relationship("ActivityEnrollment", back_populates="activity", cascade="all, delete-orphan")


class ActivityEnrollment(Base):
    """活动报名表。"""

    __tablename__ = "activity_enrollments"
    __table_args__ = (
        UniqueConstraint("activity_id", "user_id", name="uq_activity_enrollment_unique"),
    )

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="applied")
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    checked_in_at = Column(DateTime, nullable=True)

    activity = relationship("Activity", back_populates="enrollments")
    user = relationship("User")
