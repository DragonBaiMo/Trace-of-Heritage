"""资源领域的 Pydantic 模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator


class ResourceTrailCreate(BaseModel):
    """资源轨迹点创建结构。"""

    place_name: str = Field(..., min_length=1, max_length=120, description="地点名称")
    region_code: Optional[str] = Field(None, max_length=32, description="行政区划编码")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    occurred_at: Optional[datetime] = Field(None, description="发生时间")
    order_no: int = Field(..., ge=1, description="排序序号")


class ResourceTrailRead(ResourceTrailCreate):
    """轨迹点响应结构。"""

    id: int

    class Config:
        orm_mode = True


class ResourceBase(BaseModel):
    """资源公共字段。"""

    title: str = Field(..., min_length=2, max_length=120, description="资源标题")
    resource_type: str = Field(..., description="资源类型")
    synopsis: Optional[str] = Field(None, max_length=1000, description="简介")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    era: Optional[str] = Field(None, max_length=100, description="年代")
    genre: Optional[str] = Field(None, max_length=100, description="剧种流派")
    region_code: Optional[str] = Field(None, max_length=32, description="地区编码")
    author: Optional[str] = Field(None, max_length=120, description="作者/传承人")
    copyright_status: str = Field("unknown", description="版权状态")


class ResourceCreate(ResourceBase):
    """资源创建请求体。"""

    file_path: Optional[str] = Field(None, description="关联文件路径")
    external_url: Optional[str] = Field(None, description="外部链接")
    submit_for_review: bool = Field(True, description="是否立即提交审核")
    trails: list[ResourceTrailCreate] = Field(default_factory=list, description="轨迹点列表")

    @root_validator
    def validate_attachment(cls, values: dict) -> dict:
        """确保至少提供文件或外链。"""

        if not values.get("file_path") and not values.get("external_url"):
            raise ValueError("文件路径与外链需至少提供一个")
        return values


class ResourceUpdate(BaseModel):
    """资源更新请求体。"""

    title: Optional[str] = Field(None, min_length=2, max_length=120, description="资源标题")
    resource_type: Optional[str] = Field(None, description="资源类型")
    synopsis: Optional[str] = Field(None, max_length=1000, description="简介")
    tags: Optional[list[str]] = Field(None, description="标签列表")
    era: Optional[str] = Field(None, max_length=100, description="年代")
    genre: Optional[str] = Field(None, max_length=100, description="剧种流派")
    region_code: Optional[str] = Field(None, max_length=32, description="地区编码")
    author: Optional[str] = Field(None, max_length=120, description="作者/传承人")
    copyright_status: Optional[str] = Field(None, description="版权状态")
    file_path: Optional[str] = Field(None, description="文件路径")
    external_url: Optional[str] = Field(None, description="外部链接")
    status: Optional[str] = Field(None, description="资源状态")
    review_note: Optional[str] = Field(None, max_length=500, description="审核意见")
    trails: list[ResourceTrailCreate] | None = Field(None, description="轨迹点重置列表")


class ResourceRead(ResourceBase):
    """资源信息响应体。"""

    id: int
    status: str
    file_path: Optional[str]
    external_url: Optional[str]
    submitter_id: int
    reviewer_id: Optional[int]
    review_note: Optional[str]
    created_at: datetime
    updated_at: datetime
    trails: list[ResourceTrailRead] = []

    class Config:
        orm_mode = True

    @validator("tags", pre=True)
    def ensure_tags(cls, value: list[str] | None) -> list[str]:
        """确保标签以列表形式返回。"""

        if not value:
            return []
        if isinstance(value, list):
            return value
        return list(value)


class ResourceSummary(BaseModel):
    """资源概览信息。"""

    total: int
    pending: int
    approved: int
    rejected: int
    latest: list[ResourceRead]
