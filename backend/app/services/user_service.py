"""用户服务提供注册、鉴权及管理员操作。"""
from typing import Iterable, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import PasswordChange, UserCreate, UserSelfUpdate, UserUpdate
from app.utils.exceptions import BusinessException


class UserService:
    """封装用户相关的数据库操作与业务规则。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户。"""

        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, payload: UserCreate, role: str | None = None) -> User:
        """创建新用户并保存。"""

        hashed_password = get_password_hash(payload.password)
        user = User(
            username=payload.username,
            password_hash=hashed_password,
            nickname=payload.nickname,
            role=role or "user",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户名密码组合是否正确。"""

        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def list_users(self) -> Iterable[User]:
        """获取全部用户列表。"""

        return self.db.query(User).order_by(User.created_at.desc()).all()

    def update_user(self, user: User, update_data: UserUpdate) -> User:
        """更新用户信息，确保至少保留一名管理员。"""

        data = update_data.dict(exclude_unset=True)
        if data.get("role") == "admin" and user.status != "active":
            user.status = "active"
        for field, value in data.items():
            if field == "password":
                user.password_hash = get_password_hash(value)
            elif field == "status":
                user.status = value
            else:
                setattr(user, field, value)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def ensure_admin_exists(self) -> None:
        """若不存在管理员则自动创建默认管理员。"""

        admin_exists = self.db.query(User).filter(User.role == "admin").first()
        if not admin_exists:
            from app.core.config import settings

            default_payload = UserCreate(
                username=settings.default_admin_username,
                password=settings.default_admin_password,
                nickname="系统管理员",
            )
            self.create_user(default_payload, role="admin")

    def count_admins(self) -> int:
        """统计当前活跃管理员数量。"""

        return (
            self.db.query(func.count(User.id))
            .filter(User.role == "admin", User.status == "active")
            .scalar()
            or 0
        )

    # ----- Self operations -----
    def update_self(self, user: User, payload: UserSelfUpdate) -> User:
        """用户自助更新头像/昵称/简介。"""
        data = payload.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(user, field, value)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, payload: PasswordChange) -> None:
        """用户修改密码，校验原密码。"""
        if not verify_password(payload.old_password, user.password_hash):
            raise BusinessException("原密码不正确")
        user.password_hash = get_password_hash(payload.new_password)
        self.db.add(user)
        self.db.commit()

    # ----- Seed default non-admin accounts -----
    def ensure_default_accounts(self) -> None:
        """根据配置创建默认从业者与默认普通用户（若不存在）。"""
        from app.core.config import settings

        # 默认从业者
        practitioner_username = (settings.default_practitioner_username or "").strip()
        practitioner_password = (settings.default_practitioner_password or "").strip()
        if practitioner_username and practitioner_password:
            exists = (
                self.db.query(User)
                .filter(User.username == practitioner_username)
                .first()
            )
            if not exists:
                payload = UserCreate(
                    username=practitioner_username,
                    password=practitioner_password,
                    nickname="默认从业者",
                )
                self.create_user(payload, role="practitioner")

        # 默认普通用户
        user_username = (settings.default_user_username or "").strip()
        user_password = (settings.default_user_password or "").strip()
        if user_username and user_password:
            exists = (
                self.db.query(User)
                .filter(User.username == user_username)
                .first()
            )
            if not exists:
                payload = UserCreate(
                    username=user_username,
                    password=user_password,
                    nickname="默认用户",
                )
                self.create_user(payload, role="user")
