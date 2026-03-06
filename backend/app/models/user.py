"""用户模型，承担账号、角色与状态管理。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """系统用户实体，包含基础身份信息与角色。"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)
    role = Column(String(20), nullable=False, default="user")
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    resources = relationship(
        "Resource",
        back_populates="submitter",
        foreign_keys="Resource.submitter_id",
    )
    audit_logs = relationship("AuditLog", back_populates="actor")

    @property
    def is_active(self) -> bool:
        """判断账号是否处于可用状态。"""

        return self.status == "active"
