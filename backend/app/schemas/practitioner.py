"""从业者认证相关 Schema。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PractitionerApply(BaseModel):
    """从业者认证申请请求体。"""

    realname: str = Field(..., min_length=2, max_length=100, description="真实姓名")
    title: str = Field(..., min_length=2, max_length=120, description="职业或头衔")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    attachment: Optional[str] = Field(None, max_length=500, description="证明材料链接或标识")


class PractitionerReview(BaseModel):
    """管理员审核从业者申请。"""

    decision: str = Field(..., description="approve 或 reject")
    review_note: Optional[str] = Field(None, max_length=500, description="审核意见")


class PractitionerApplicationRead(BaseModel):
    """从业者认证申请响应。"""

    id: int
    realname: str
    title: str
    bio: Optional[str]
    attachment: Optional[str]
    status: str
    applicant_id: int
    reviewer_id: Optional[int]
    review_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
