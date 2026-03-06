"""活动领域模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class ActivityBase(BaseModel):
    """活动公共字段。"""

    title: str = Field(..., min_length=2, max_length=120, description="活动标题")
    description: str = Field(..., min_length=10, description="活动说明")
    location: str = Field(..., min_length=2, max_length=255, description="活动地点")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    quota: int = Field(..., ge=1, le=1000, description="人数上限")

    @validator("end_time")
    def validate_time(cls, end: datetime, values: dict) -> datetime:
        """校验结束时间需晚于开始时间。"""

        start = values.get("start_time")
        if start and end <= start:
            raise ValueError("结束时间需晚于开始时间")
        return end


class ActivityCreate(ActivityBase):
    """活动创建请求体。"""

    submit_for_review: bool = Field(True, description="是否提交审核")


class ActivityReview(BaseModel):
    """活动审核请求体。"""

    decision: str = Field(..., description="审核决策 approve/reject")
    review_note: Optional[str] = Field(None, min_length=5, description="审核意见")


class ActivityRead(ActivityBase):
    """活动响应结构。"""

    id: int
    status: str
    creator_id: int
    reviewer_id: Optional[int]
    review_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EnrollmentRead(BaseModel):
    """报名信息响应体。"""

    id: int
    activity_id: int
    user_id: int
    status: str
    applied_at: datetime
    checked_in_at: Optional[datetime]

    class Config:
        orm_mode = True
