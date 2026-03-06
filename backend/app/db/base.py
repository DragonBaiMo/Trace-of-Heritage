"""数据库基础模型定义入口。"""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_tables(engine: Engine) -> None:
    """创建当前元数据中的全部数据表。"""

    metadata = getattr(Base, "metadata", None)
    if metadata is not None:
        metadata.create_all(bind=engine)

# 导入模型以便 Alembic/FastAPI 创建表结构时自动发现
from app import models  # noqa: F401,E402  # pylint: disable=unused-import
