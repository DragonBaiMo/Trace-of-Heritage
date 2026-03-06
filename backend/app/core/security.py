"""安全与鉴权相关工具。"""
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 新哈希统一使用 pbkdf2_sha512，保留 pbkdf2_sha256/bcrypt 做历史兼容校验
# 可兼容旧库并规避部分 Windows 环境下 bcrypt 后端异常导致的登录失败
pwd_context = CryptContext(schemes=["pbkdf2_sha512", "pbkdf2_sha256", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验用户输入的明文密码与存储散列值是否一致。"""

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 当历史哈希算法未知或哈希串损坏时，按校验失败处理，避免抛出 500
        return False


def get_password_hash(password: str) -> str:
    """生成密码散列值。"""

    return pwd_context.hash(password)


def needs_password_rehash(hashed_password: str) -> bool:
    """判断现有密码哈希是否需要升级到当前首选算法。"""

    return pwd_context.needs_update(hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """根据给定载荷生成 JWT 访问令牌。"""

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """解析 JWT 令牌，当出现异常时返回 None。"""

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
