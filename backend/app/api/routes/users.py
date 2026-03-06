"""用户相关接口。"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import PasswordChange, UserRead, UserSelfUpdate, UserUpdate
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=ResponseModel[UserRead])
def read_current_user(current_user: User = Depends(get_current_user)) -> ResponseModel[UserRead]:
    """查询当前登录用户信息。"""

    return ResponseModel(code=0, message=MESSAGES["profile_success"], data=UserRead.from_orm(current_user))


@router.patch("/me", response_model=ResponseModel[UserRead])
def update_self(
    payload: UserSelfUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[UserRead]:
    """用户自助更新昵称/头像/简介。"""
    service = UserService(db)
    updated = service.update_self(current_user, payload)
    AuditService(db).record(
        actor_id=current_user.id,
        action="update_self",
        target_type="user",
        target_id=str(current_user.id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["profile_updated"], data=UserRead.from_orm(updated))


@router.post("/me/password", response_model=ResponseModel[None])
def change_password(
    payload: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[None]:
    """用户修改密码，需要校验原密码。"""
    service = UserService(db)
    try:
        service.change_password(current_user, payload)
    except Exception as exc:  # 捕获 BusinessException 中的提示
        detail = str(exc)
        if detail == MESSAGES.get("password_incorrect", "原密码不正确"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
        raise
    AuditService(db).record(
        actor_id=current_user.id,
        action="change_password",
        target_type="user",
        target_id=str(current_user.id),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message="密码修改成功", data=None)


@router.get("/", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[list[UserRead]])
def list_users(db: Session = Depends(get_db_session)) -> ResponseModel[list[UserRead]]:
    """管理员获取全部用户列表。"""

    users = UserService(db).list_users()
    return ResponseModel(code=0, message=MESSAGES["user_list"], data=[UserRead.from_orm(u) for u in users])


@router.patch("/{user_id}", dependencies=[Depends(require_roles("admin"))], response_model=ResponseModel[UserRead])
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db_session),
    current_admin: User = Depends(get_current_user),
) -> ResponseModel[UserRead]:
    """管理员调整用户角色或状态，并写入审计日志。"""

    service = UserService(db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.role == "admin" and payload.status == "frozen":
        if service.count_admins() <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="必须保留至少一名管理员")
    updated_user = service.update_user(user, payload)
    AuditService(db).record(
        actor_id=current_admin.id,
        action="update_user",
        target_type="user",
        target_id=str(user_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["user_updated"], data=UserRead.from_orm(updated_user))
