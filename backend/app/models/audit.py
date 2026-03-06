"""审计日志模型，用于记录关键操作行为。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditLog(Base):
    """审计日志实体，存储操作人、动作、目标、备注与来源 IP 等信息。"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(64), nullable=False)
    target_type = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=False)
    note = Column(Text, nullable=True)
    ip = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    actor = relationship("User", back_populates="audit_logs")
