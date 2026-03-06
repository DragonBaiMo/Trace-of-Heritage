"""安全与鉴权相关工具。"""
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 优先使用 pbkdf2_sha256 生成新哈希，同时保留 bcrypt 以兼容历史哈希验证
# 这样可规避部分 Windows 环境下 bcrypt 后端加载异常导致的登录失败问题
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验用户输入的明文密码与存储散列值是否一致。"""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码散列值。"""

    return pwd_context.hash(password)


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
