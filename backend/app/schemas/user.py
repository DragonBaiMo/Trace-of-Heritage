"""用户相关 Pydantic 模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class UserBase(BaseModel):
    """用户公共字段。"""

    username: str = Field(..., min_length=4, max_length=20, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserCreate(UserBase):
    """用户注册请求体。"""

    password: str = Field(..., min_length=8, description="登录密码")

    @validator("password")
    def validate_password(cls, value: str) -> str:
        """校验密码复杂度，需包含字母与数字。"""

        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("密码需同时包含字母与数字")
        return value


class UserUpdate(BaseModel):
    """管理员调整用户信息请求体。"""

    username: Optional[str] = Field(None, min_length=4, max_length=20, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像地址")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    role: Optional[str] = Field(None, description="角色")
    status: Optional[str] = Field(None, description="账号状态")
    password: Optional[str] = Field(None, min_length=8, description="重置密码")


class UserRead(BaseModel):
    """用户信息响应体。"""

    id: int
    username: str
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserSelfUpdate(BaseModel):
    """用户自助更新资料请求体。"""

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像地址")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class PasswordChange(BaseModel):
    """修改密码请求体。"""

    old_password: str = Field(..., min_length=8, description="原密码")
    new_password: str = Field(..., min_length=8, description="新密码，需包含字母与数字")
