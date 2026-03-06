"""通用响应模型定义，统一接口返回结构。"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """标准响应结构，包含编码、提示信息与数据。"""

    code: int
    message: str
    data: Optional[T] = None
    meta: Optional[Any] = None


class PaginationMeta(BaseModel):
    """分页元信息结构体。"""

    page: int
    page_size: int
    total: int
