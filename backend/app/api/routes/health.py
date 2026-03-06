"""健康检查路由，用于部署时快速验证服务状态。"""
from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("/", response_model=ResponseModel[dict])
def read_health() -> ResponseModel[dict]:
    """返回应用名称与版本，确认服务可用。"""

    return ResponseModel(code=0, message="服务可用", data={"name": settings.app_name, "version": settings.app_version})
