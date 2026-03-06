"""FastAPI 应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    activities,
    ai,
    audits,
    auth,
    export,
    health,
    posts,
    quiz,
    recommendations,
    resources,
    shop,
    stats,
    users,
    practitioners,
    wiki,
)
from app.core.config import settings
from app.db import base  # noqa: F401
from app.db.session import engine
from app.db.migrations import run_startup_migrations
from app.services.user_service import UserService

# 创建数据库表结构前执行兼容迁移
run_startup_migrations(engine)
# 创建数据库表结构
base.create_tables(engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)

# 允许本地开发常见跨域场景
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_admin() -> None:
    """应用启动时确保存在至少一名管理员。"""

    from app.db.session import SessionLocal

    with SessionLocal() as session:
        svc = UserService(session)
        svc.ensure_admin_exists()
        # 按 .env 配置创建默认从业者与默认普通用户（若不存在）
        svc.ensure_default_accounts()


app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(audits.router, prefix="/api")
app.include_router(practitioners.router, prefix="/api")
app.include_router(wiki.router, prefix="/api")
app.include_router(shop.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(export.router, prefix="/api")
