"""数据库会话管理模块，负责创建 SQLAlchemy Session 工厂。"""
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.sqlite_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_schema_guard_lock = Lock()


def ensure_schema_ready() -> None:
    """在会话创建前确保关键表已存在，避免运行中因数据库文件变更导致缺表。"""

    with _schema_guard_lock:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users' LIMIT 1")
            ).first()
            if result is not None:
                return

        # 延迟导入避免模块初始化阶段的循环依赖
        from app.db import base
        from app.db.migrations import run_startup_migrations

        run_startup_migrations(engine)
        base.create_tables(engine)


def get_db():
    """FastAPI 依赖函数：提供数据库会话并确保请求结束后关闭。"""

    ensure_schema_ready()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
