"""测试基线配置，提供 TestClient 与独立数据库。"""
import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TestClient]:
    """构建指向临时数据库的 FastAPI 客户端。"""

    base_dir = Path(__file__).resolve().parents[1]
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    data_dir = tmp_path_factory.mktemp("data")
    db_path = data_dir / "test.db"
    os.environ["SQLITE_PATH"] = str(db_path)
    os.environ["DEFAULT_ADMIN_USERNAME"] = "admin"
    os.environ["DEFAULT_ADMIN_PASSWORD"] = "Admin123"
    os.environ["DEFAULT_PRACTITIONER_USERNAME"] = "opera_practitioner"
    os.environ["DEFAULT_PRACTITIONER_PASSWORD"] = "Practitioner123"
    os.environ["DEFAULT_USER_USERNAME"] = "heritage_user"
    os.environ["DEFAULT_USER_PASSWORD"] = "Heritage123"

    from importlib import reload

    from app.core import config

    reload(config)
    config.reload_settings()

    from app.main import app
    from app.db.session import SessionLocal
    from app.services.user_service import UserService

    with SessionLocal() as session:
        user_service = UserService(session)
        user_service.ensure_admin_exists()
        user_service.ensure_default_accounts()

    client = TestClient(app)
    yield client
    # 清理测试数据库文件
    if db_path.exists():
        db_path.unlink()
    data_dir.rmdir()
