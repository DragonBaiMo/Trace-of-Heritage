"""统计接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.schemas.common import ResponseModel
from app.schemas.stats import DashboardStats
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["统计"], dependencies=[Depends(require_roles("admin", "practitioner"))])


@router.get("/dashboard", response_model=ResponseModel[DashboardStats])
def load_dashboard(db: Session = Depends(get_db_session)) -> ResponseModel[DashboardStats]:
    """获取统计看板数据。"""

    stats = StatsService(db).load_dashboard()
    return ResponseModel(code=0, message=MESSAGES["stats_loaded"], data=stats)
