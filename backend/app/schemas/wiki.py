"""百科 schema。"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WikiEntryRead(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str]
    status: str
    author_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WikiEntryQuery(BaseModel):
    keyword: Optional[str] = Field(None, description="关键字")
    category: Optional[str] = Field(None, description="分类")
