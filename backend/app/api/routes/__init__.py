"""路由模块聚合，便于主程序统一引入。"""
from app.api.routes import activities, ai, audits, auth, export, health, posts, quiz, recommendations, resources, stats, users, practitioners  # noqa: F401

__all__ = [
    "activities",
    "ai",
    "audits",
    "auth",
    "export",
    "health",
    "posts",
    "quiz",
    "recommendations",
    "resources",
    "stats",
    "users",
    "practitioners",
]
