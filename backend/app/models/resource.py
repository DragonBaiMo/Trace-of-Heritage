"""文化资源模型，记录上传者提交的内容。"""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Resource(Base):
    """资源实体包含完整的元数据与审核字段。"""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    resource_type = Column(String(20), nullable=False)
    file_path = Column(String(255), nullable=True)
    external_url = Column(String(255), nullable=True)
    synopsis = Column(Text, nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    era = Column(String(100), nullable=True)
    genre = Column(String(100), nullable=True)
    region_code = Column(String(32), nullable=True)
    author = Column(String(120), nullable=True)
    copyright_status = Column(String(20), nullable=False, default="unknown")
    status = Column(String(20), nullable=False, default="draft")
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    submitter = relationship("User", back_populates="resources", foreign_keys=[submitter_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    trails = relationship("ResourceGeoTrail", back_populates="resource", cascade="all, delete-orphan")


class ResourceGeoTrail(Base):
    """资源的地理传播轨迹点。"""

    __tablename__ = "resource_geo_trails"
    __table_args__ = (UniqueConstraint("resource_id", "order_no", name="uq_resource_trail_order"),)

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    place_name = Column(String(120), nullable=False)
    region_code = Column(String(32), nullable=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    occurred_at = Column(DateTime, nullable=True)
    order_no = Column(Integer, nullable=False)

    resource = relationship("Resource", back_populates="trails")
