"""从业者认证路由。"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.practitioner import PractitionerApplication
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.practitioner import (
    PractitionerApply,
    PractitionerApplicationRead,
    PractitionerReview,
)
from app.services.audit_service import AuditService
from app.services.practitioner_service import PractitionerService
from app.utils.exceptions import BusinessException
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/practitioners", tags=["从业者认证"])


@router.post("/apply", response_model=ResponseModel[PractitionerApplicationRead])
def apply(
    payload: PractitionerApply,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[PractitionerApplicationRead]:
    """用户提交从业者认证申请。"""
    service = PractitionerService(db)
    try:
        app = service.apply(current_user.id, payload)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action="practitioner_apply",
        target_type="practitioner_application",
        target_id=str(app.id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["pract_apply_success"], data=PractitionerApplicationRead.from_orm(app))


@router.get(
    "/applications",
    dependencies=[Depends(require_roles("admin"))],
    response_model=ResponseModel[list[PractitionerApplicationRead]],
)
def list_applications(
    status: str | None = Query(
        default=None,
        description="按状态过滤，允许 pending/approved/rejected",
        pattern="^(pending|approved|rejected)$",
    ),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[PractitionerApplicationRead]]:
    """管理员查看全部认证申请。"""
    apps = PractitionerService(db).list_applications(status)
    return ResponseModel(
        code=0,
        message=MESSAGES["pract_list"],
        data=[PractitionerApplicationRead.from_orm(a) for a in apps],
    )


@router.post(
    "/applications/{application_id}/review",
    dependencies=[Depends(require_roles("admin"))],
    response_model=ResponseModel[PractitionerApplicationRead],
)
def review_application(
    application_id: int,
    payload: PractitionerReview,
    request: Request,
    current_admin: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[PractitionerApplicationRead]:
    """管理员审核从业者申请。"""
    application = db.query(PractitionerApplication).filter(PractitionerApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    try:
        updated = PractitionerService(db).review(application, payload.decision, payload.review_note, current_admin.id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    AuditService(db).record(
        actor_id=current_admin.id,
        action=f"practitioner_review_{payload.decision}",
        target_type="practitioner_application",
        target_id=str(application_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["pract_reviewed"], data=PractitionerApplicationRead.from_orm(updated))
