"""鉴权相关模型。"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT 访问令牌结构。"""

    access_token: str = Field(..., description="访问令牌字符串")
    token_type: str = Field("bearer", description="令牌类型")


class LoginRequest(BaseModel):
    """登录请求体。"""

    username: str = Field(..., min_length=4, max_length=20, description="用户名")
    password: str = Field(..., min_length=8, description="密码")
