"""互动领域相关模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """帖子基础字段，供复用定义。"""

    title: Optional[str] = Field(None, min_length=2, max_length=120, description="帖子标题")
    content_md: Optional[str] = Field(None, min_length=10, description="Markdown 内容")
    topic: Optional[str] = Field(None, max_length=120, description="所属话题")


class PostCreate(PostBase):
    """帖子创建请求体。"""

    title: str = Field(..., min_length=2, max_length=120, description="帖子标题")
    content_md: str = Field(..., min_length=10, description="Markdown 内容")
    submit_for_review: bool = Field(True, description="是否提交审核")


class PostUpdate(PostBase):
    """帖子更新请求体。"""

    status: Optional[str] = Field(None, description="状态")
    review_note: Optional[str] = Field(None, max_length=500, description="审核意见")


class PostRead(PostBase):
    """帖子响应结构。"""

    title: str = Field(..., min_length=2, max_length=120, description="帖子标题")
    content_md: str = Field(..., min_length=10, description="Markdown 内容")
    id: int
    status: str
    like_count: int
    favorite_count: int
    author_id: int
    reviewer_id: Optional[int]
    review_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    """评论创建请求体。"""

    content: str = Field(..., min_length=2, max_length=500, description="评论内容")


class CommentRead(BaseModel):
    """评论响应体。"""

    id: int
    post_id: int
    author_id: int
    content: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class ReactionRequest(BaseModel):
    """点赞收藏请求体。"""

    reaction_type: str = Field(..., description="like 或 favorite")
    target_type: str = Field(..., description="post 或 resource")
    target_id: int = Field(..., ge=1, description="目标 ID")
