"""统计看板相关模型。"""
from datetime import date
from typing import List

from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    """折线图节点。"""

    day: date = Field(..., description="日期")
    count: int = Field(..., ge=0, description="数量")


class CategoryValue(BaseModel):
    """分类数值。"""

    name: str
    value: int


class ActivityStat(BaseModel):
    """活动参与统计。"""

    title: str
    enrolled: int
    checked_in: int


class DashboardStats(BaseModel):
    """统计看板总数据。"""

    resource_trend: List[TrendPoint]
    topic_hot: List[CategoryValue]
    region_distribution: List[CategoryValue]
    activity_participants: List[ActivityStat]
