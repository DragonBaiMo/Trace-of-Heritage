"""审计日志接口，提供管理员查看操作记录的能力。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_role
from app.localization.messages import MESSAGES
from app.schemas.audit import AuditLogRead
from app.schemas.common import ResponseModel
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audits", tags=["审计"], dependencies=[Depends(require_role("admin"))])


@router.get("/", response_model=ResponseModel[list[AuditLogRead]])
def list_audit_logs(
    limit: int = Query(20, ge=1, le=200, description="返回的最大记录数"),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[AuditLogRead]]:
    """按时间倒序返回审计日志列表。"""

    logs = AuditService(db).list_logs(limit=limit)
    return ResponseModel(
        code=0,
        message=MESSAGES["audit_list"],
        data=[AuditLogRead.from_orm(item) for item in logs],
    )
