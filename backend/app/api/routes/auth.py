"""鉴权路由。"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.config import settings
from app.core.security import create_access_token
from app.localization.messages import MESSAGES
from app.schemas.auth import LoginRequest, Token
from app.schemas.common import ResponseModel
from app.schemas.user import UserCreate, UserRead
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/auth", tags=["鉴权"])


@router.post("/register", response_model=ResponseModel[UserRead])
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db_session)) -> ResponseModel[UserRead]:
    """注册接口，创建普通用户并写入审计日志。"""

    service = UserService(db)
    existing = service.get_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册")
    user = service.create_user(payload)
    AuditService(db).record(
        actor_id=user.id,
        action="register",
        target_type="user",
        target_id=str(user.id),
        note=payload.json(exclude={"password"}, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["register_success"], data=UserRead.from_orm(user))


@router.post("/token", response_model=Token)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
) -> Token:
    """OAuth2 兼容的密码模式登录端点。"""

    service = UserService(db)
    user = service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGES["credential_error"])
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MESSAGES["inactive_account"])
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    AuditService(db).record(
        actor_id=user.id,
        action="login",
        target_type="user",
        target_id=str(user.id),
        ip=extract_client_ip(request),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=ResponseModel[Token])
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db_session)) -> ResponseModel[Token]:
    """为前端提供 JSON 登录能力。"""

    service = UserService(db)
    user = service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGES["credential_error"])
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MESSAGES["inactive_account"])
    access_token = create_access_token(data={"sub": user.username})
    AuditService(db).record(
        actor_id=user.id,
        action="login",
        target_type="user",
        target_id=str(user.id),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["login_success"], data=Token(access_token=access_token, token_type="bearer"))
