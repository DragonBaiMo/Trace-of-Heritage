"""审计日志响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogRead(BaseModel):
    """审计日志只读结构。"""

    id: int
    actor_id: int
    action: str = Field(..., description="动作标识")
    target_type: str = Field(..., description="目标类型")
    target_id: str = Field(..., description="目标标识")
    note: str | None = Field(None, description="操作备注")
    ip: str | None = Field(None, description="发起操作的客户端 IP")
    created_at: datetime

    class Config:
        orm_mode = True
