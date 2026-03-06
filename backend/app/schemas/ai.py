"""AI 相关的请求与响应模型。"""
from pydantic import BaseModel, Field


class AISynopsisRequest(BaseModel):
    """AI 简介生成请求体。"""

    content: str = Field(..., min_length=20, description="待提炼的剧本文本")
    expect_length: int = Field(100, ge=50, le=300, description="期望简介字数")


class AISynopsisResponse(BaseModel):
    """AI 简介生成响应体。"""

    synopsis: str
    tags: list[str]
