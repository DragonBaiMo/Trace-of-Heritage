"""活动接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityRead, ActivityReview, EnrollmentRead
from app.schemas.common import PaginationMeta, ResponseModel
from app.services.activity_service import ActivityService
from app.services.audit_service import AuditService
from app.utils.exceptions import BusinessException
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/activities", tags=["活动"])


@router.post("/", response_model=ResponseModel[ActivityRead], dependencies=[Depends(require_roles("practitioner", "admin"))])
def create_activity(
    payload: ActivityCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[ActivityRead]:
    """创建活动。"""

    service = ActivityService(db)
    activity = service.create_activity(payload, current_user.id)
    AuditService(db).record(
        actor_id=current_user.id,
        action="create_activity",
        target_type="activity",
        target_id=str(activity.id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["activity_created"], data=ActivityRead.from_orm(activity))


@router.get("/", response_model=ResponseModel[list[ActivityRead]])
def list_activities(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ActivityRead]]:
    """分页查询活动。"""

    service = ActivityService(db)
    activities, total = service.list_activities(
        status=status_filter,
        page=page,
        page_size=page_size,
        current_user_role=current_user.role,
        current_user_id=current_user.id,
    )
    return ResponseModel(
        code=0,
        message=MESSAGES["activity_list"],
        data=[ActivityRead.from_orm(item) for item in activities],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/enrollments/me", response_model=ResponseModel[list[ActivityRead]])
def list_my_enrollments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ActivityRead]]:
    """返回当前用户已报名的活动列表。"""

    service = ActivityService(db)
    items, total = service.list_user_enrolled_activities(user_id=current_user.id, page=page, page_size=page_size)
    return ResponseModel(
        code=0,
        message=MESSAGES["activity_list"],
        data=[ActivityRead.from_orm(item) for item in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.post(
    "/{activity_id}/review",
    dependencies=[Depends(require_roles("admin"))],
    response_model=ResponseModel[ActivityRead],
)
def review_activity(
    activity_id: int,
    payload: ActivityReview,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[ActivityRead]:
    """审核活动。"""

    service = ActivityService(db)
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["activity_not_found"])
    try:
        updated = service.review_activity(activity, payload.decision, payload.review_note, current_user.id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action=f"review_activity_{payload.decision}",
        target_type="activity",
        target_id=str(activity_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["activity_reviewed"], data=ActivityRead.from_orm(updated))


@router.post(
    "/{activity_id}/enroll",
    response_model=ResponseModel[EnrollmentRead],
)
def enroll_activity(
    activity_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[EnrollmentRead]:
    """报名活动。"""

    service = ActivityService(db)
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["activity_not_found"])
    try:
        enrollment = service.enroll(activity, current_user.id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=exc.message) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action="enroll",
        target_type="activity",
        target_id=str(activity_id),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["enroll_success"], data=EnrollmentRead.from_orm(enrollment))


@router.post(
    "/{activity_id}/checkin",
    response_model=ResponseModel[EnrollmentRead],
)
def checkin_activity(
    activity_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[EnrollmentRead]:
    """签到活动。"""

    service = ActivityService(db)
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["activity_not_found"])
    try:
        enrollment = service.check_in(activity, current_user.id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action="checkin",
        target_type="activity",
        target_id=str(activity_id),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["checkin_success"], data=EnrollmentRead.from_orm(enrollment))
