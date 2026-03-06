"""应用配置模块。"""
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """系统运行所需的基础配置。"""

    app_name: str = Field("Trace of Heritage API", description="应用名称")
    app_version: str = Field("0.2.0", description="应用版本号")
    secret_key: str = Field("change_me", description="JWT 签名密钥")
    algorithm: str = Field("HS256", description="JWT 加密算法")
    access_token_expire_minutes: int = Field(60 * 24, description="访问令牌有效时间，分钟")
    sqlite_path: str = Field("data/app.db", description="SQLite 数据库文件路径")
    default_admin_username: str = Field("admin", description="默认管理员账号")
    default_admin_password: str = Field("Admin123", description="默认管理员密码")
    # 兼容历史环境变量：若设置了 DEFAULT_ADMIN_EMAIL 且未显式提供用户名，则以该值作为用户名
    default_admin_email: str | None = Field(None, description="兼容：默认管理员邮箱（等同于用户名）")
    # 可选：默认从业者与默认普通用户（首次启动时若不存在则创建）
    default_practitioner_username: str | None = Field(
        "opera_practitioner",
        description="默认从业者账号（用于开发/演示环境）",
    )
    default_practitioner_password: str | None = Field(
        "Practitioner123",
        description="默认从业者密码（用于开发/演示环境）",
    )
    default_user_username: str | None = Field(
        "heritage_user",
        description="默认普通用户账号（用于开发/演示环境）",
    )
    default_user_password: str | None = Field(
        "Heritage123",
        description="默认普通用户密码（用于开发/演示环境）",
    )
    media_root: str = Field("data/uploads", description="上传文件根目录，支持相对路径")
    ai_base_url: str = Field(
        "https://api.siliconflow.cn/v1/chat/completions",
        description="大模型接口地址",
    )
    ai_model: str = Field(
        "Qwen/Qwen3-Omni-30B-A3B-Instruct",
        description="大模型名称",
    )
    ai_api_key: str | None = Field(None, description="大模型访问密钥（必填，否则仅提供占位实现）")
    ai_timeout: int = Field(30, description="大模型请求超时时间（秒）")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置实例，首次调用时确保数据库目录存在。"""

    settings = Settings()

    # 1) 兼容 DEFAULT_ADMIN_EMAIL 作为用户名
    if settings.default_admin_email and (not settings.default_admin_username or settings.default_admin_username == "admin"):
        settings.default_admin_username = settings.default_admin_email

    # 2) 将 sqlite_path 解析为以 backend 目录为基准的绝对路径，避免工作目录变化
    base_dir = Path(__file__).resolve().parents[2]  # backend 目录
    db_path = Path(settings.sqlite_path)
    if not db_path.is_absolute():
        db_path = base_dir / db_path
    # 规范化并回写
    settings.sqlite_path = str(db_path)

    data_dir = db_path.parent
    data_dir.mkdir(parents=True, exist_ok=True)

    media_root = Path(settings.media_root)
    if not media_root.is_absolute():
        media_root = base_dir / media_root
    settings.media_root = str(media_root)
    media_root.mkdir(parents=True, exist_ok=True)

    try:
        print(f"[CONFIG] Using SQLite at: {db_path}")
    except Exception:
        pass
    return settings


def reload_settings() -> Settings:
    """清除缓存并重新加载配置。"""

    get_settings.cache_clear()
    new_settings = get_settings()
    globals()["settings"] = new_settings
    return new_settings


settings = get_settings()
