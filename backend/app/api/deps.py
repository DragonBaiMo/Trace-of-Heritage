"""FastAPI 依赖项。"""
from collections.abc import Generator
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.localization.messages import MESSAGES
from app.models.user import User
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_db_session() -> Generator[Session, None, None]:
    """提供数据库 Session。"""

    yield from get_db()


def get_current_user(db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)) -> User:
    """解析 JWT 获取当前用户，若令牌无效则抛出异常。"""

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGES["credential_error"])
    user_service = UserService(db)
    user = user_service.get_by_username(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGES["inactive_account"])
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    """检查当前用户是否具备指定角色之一。"""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MESSAGES["permission_denied"])
        return current_user

    return checker


def require_role(role: str) -> Callable[[User], User]:
    """兼容旧签名的单角色检查。"""

    return require_roles(role)
