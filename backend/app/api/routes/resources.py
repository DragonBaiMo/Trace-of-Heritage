"""资源相关接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.resource import Resource, ResourceGeoTrail
from app.models.user import User
from app.schemas.common import PaginationMeta, ResponseModel
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceSummary, ResourceTrailRead, ResourceUpdate
from app.services.audit_service import AuditService
from app.services.resource_service import ResourceService
from app.utils.exceptions import BusinessException
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/resources", tags=["资源"])


@router.post("/", response_model=ResponseModel[ResourceRead])
def create_resource(
    payload: ResourceCreate,
    request: Request,
    current_user: User = Depends(require_roles("practitioner", "admin")),
    db: Session = Depends(get_db_session),
) -> ResponseModel[ResourceRead]:
    """提交或保存资源草稿。"""

    service = ResourceService(db)
    resource, watermark_warning = service.create_resource(payload, current_user.id)
    AuditService(db).record(
        actor_id=current_user.id,
        action="create_resource",
        target_type="resource",
        target_id=str(resource.id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    db.refresh(resource)
    message = MESSAGES["resource_created"]
    if watermark_warning:
        message = f"{message}（{watermark_warning}）"
    return ResponseModel(code=0, message=message, data=_to_read(resource))


@router.get("/", response_model=ResponseModel[list[ResourceRead]])
def list_resources(
    status: Optional[str] = Query(None, description="资源状态筛选"),
    keyword: Optional[str] = Query(None, description="标题或描述关键词"),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ResourceRead]]:
    """查询资源列表，可按状态与关键词过滤并支持分页。"""

    service = ResourceService(db)
    resources, total = service.list_resources(
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size,
        current_user_role=current_user.role,
        current_user_id=current_user.id,
    )
    return ResponseModel(
        code=0,
        message=MESSAGES["resource_list"],
        data=[_to_read(r) for r in resources],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/summary", response_model=ResponseModel[ResourceSummary])
def summarize_resources(db: Session = Depends(get_db_session)) -> ResponseModel[ResourceSummary]:
    """提供资源数量与最新动态概览。"""

    summary = ResourceService(db).summarize()
    return ResponseModel(
        code=0,
        message=MESSAGES["resource_summary"],
        data=ResourceSummary(
            total=summary["total"],
            pending=summary["pending"],
            approved=summary["approved"],
            rejected=summary["rejected"],
            latest=[_to_read(item) for item in summary["latest"]],
        ),
    )


@router.get("/{resource_id}", response_model=ResponseModel[ResourceRead])
def get_resource(resource_id: int, db: Session = Depends(get_db_session)) -> ResponseModel[ResourceRead]:
    """获取资源详情。"""

    resource = ResourceService(db).get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["resource_not_found"])
    return ResponseModel(code=0, message=MESSAGES["resource_detail"], data=_to_read(resource))


@router.patch(
    "/{resource_id}",
    dependencies=[Depends(require_roles("admin", "practitioner"))],
    response_model=ResponseModel[ResourceRead],
)
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[ResourceRead]:
    """管理员或提交者更新资源信息。"""

    service = ResourceService(db)
    resource = service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["resource_not_found"])
    if current_user.role != "admin" and resource.submitter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MESSAGES["permission_denied"])
    try:
        updated_resource, watermark_warning = service.update_resource(
            resource,
            payload,
            reviewer_id=current_user.id if current_user.role == "admin" else None,
        )
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action="update_resource",
        target_type="resource",
        target_id=str(resource_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    message = MESSAGES["resource_updated"]
    if watermark_warning:
        message = f"{message}（{watermark_warning}）"
    return ResponseModel(code=0, message=message, data=_to_read(updated_resource))


@router.post(
    "/{resource_id}/review",
    dependencies=[Depends(require_roles("admin"))],
    response_model=ResponseModel[ResourceRead],
)
def review_resource(
    resource_id: int,
    request: Request,
    decision: str = Query(..., description="审核决策 approve/reject"),
    review_note: Optional[str] = Query(None, description="审核意见"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[ResourceRead]:
    """管理员审核资源。"""

    resource = ResourceService(db).get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MESSAGES["resource_not_found"])
    try:
        updated = ResourceService(db).review_resource(resource, decision, review_note, current_user.id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    AuditService(db).record(
        actor_id=current_user.id,
        action=f"review_resource_{decision}",
        target_type="resource",
        target_id=str(resource_id),
        note=review_note,
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["resource_reviewed"], data=_to_read(updated))


@router.get("/{resource_id}/trails", response_model=ResponseModel[list[ResourceTrailRead]])
def list_resource_trails(resource_id: int, db: Session = Depends(get_db_session)) -> ResponseModel[list[ResourceTrailRead]]:
    """获取资源的轨迹点数据。"""

    service = ResourceService(db)
    try:
        trails: list[ResourceGeoTrail] = service.list_trails(resource_id)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    return ResponseModel(
        code=0,
        message=MESSAGES["resource_trail_list"],
        data=[
            ResourceTrailRead(
                id=trail.id,
                place_name=trail.place_name,
                region_code=trail.region_code,
                longitude=trail.longitude,
                latitude=trail.latitude,
                occurred_at=trail.occurred_at,
                order_no=trail.order_no,
            )
            for trail in trails
        ],
    )


def _to_read(resource: Resource) -> ResourceRead:
    """帮助方法，将 ORM 对象转换为响应模型。"""

    return ResourceRead(
        id=resource.id,
        title=resource.title,
        resource_type=resource.resource_type,
        synopsis=resource.synopsis,
        tags=resource.tags or [],
        era=resource.era,
        genre=resource.genre,
        region_code=resource.region_code,
        author=resource.author,
        copyright_status=resource.copyright_status,
        status=resource.status,
        file_path=resource.file_path,
        external_url=resource.external_url,
        submitter_id=resource.submitter_id,
        reviewer_id=resource.reviewer_id,
        review_note=resource.review_note,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
        trails=[
            ResourceTrailRead(
                id=trail.id,
                place_name=trail.place_name,
                region_code=trail.region_code,
                longitude=trail.longitude,
                latitude=trail.latitude,
                occurred_at=trail.occurred_at,
                order_no=trail.order_no,
            )
            for trail in sorted(resource.trails, key=lambda item: item.order_no)
        ],
    )
