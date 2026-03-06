"""数据库结构迁移工具，保障旧数据结构与最新模型兼容。"""
from __future__ import annotations

import logging
from typing import Set

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def run_startup_migrations(engine: Engine) -> None:
    """执行启动期必要的结构迁移，避免旧字段导致服务异常。"""

    inspector = inspect(engine)
    table_names: Set[str] = set(inspector.get_table_names())

    if "users" in table_names:
        columns: Set[str] = {column["name"] for column in inspector.get_columns("users")}

        needs_username = "username" not in columns and "email" in columns
        needs_password_hash = "password_hash" not in columns and "hashed_password" in columns
        needs_nickname = "nickname" not in columns and "name" in columns
        needs_avatar = "avatar" not in columns
        needs_bio = "bio" not in columns
        needs_status = "status" not in columns

        if any([needs_username, needs_password_hash, needs_nickname, needs_avatar, needs_bio, needs_status]):
            logger.info("检测到 users 表存在旧字段，开始执行兼容迁移。")

            with engine.begin() as connection:
                if needs_username:
                    connection.execute(text("ALTER TABLE users RENAME COLUMN email TO username"))
                if needs_password_hash:
                    connection.execute(text("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash"))
                if needs_nickname:
                    connection.execute(text("ALTER TABLE users RENAME COLUMN name TO nickname"))
                if needs_avatar:
                    connection.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(255)"))
                if needs_bio:
                    connection.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(500)"))
                if needs_status:
                    connection.execute(
                        text("ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'")
                    )
                    if "is_active" in columns:
                        connection.execute(
                            text("UPDATE users SET status = CASE WHEN COALESCE(is_active, 1) = 1 THEN 'active' ELSE 'inactive' END")
                        )

            logger.info("users 表结构迁移完成。")

    if "audit_logs" in table_names:
        audit_columns: Set[str] = {column["name"] for column in inspector.get_columns("audit_logs")}
        needs_note = "note" not in audit_columns
        needs_ip = "ip" not in audit_columns

        if needs_note or needs_ip:
            logger.info("检测到 audit_logs 表缺少新列，准备补全 note/ip 字段。")

            with engine.begin() as connection:
                if needs_note:
                    connection.execute(text("ALTER TABLE audit_logs ADD COLUMN note TEXT"))
                if needs_ip:
                    connection.execute(text("ALTER TABLE audit_logs ADD COLUMN ip VARCHAR(45)"))

            logger.info("audit_logs 表结构迁移完成。")

    if "orders" in table_names:
        order_columns: Set[str] = {column["name"] for column in inspector.get_columns("orders")}
        needs_shipping = "shipping_remark" not in order_columns
        needs_shipped_at = "shipped_at" not in order_columns
        needs_confirmed_at = "confirmed_at" not in order_columns
        needs_status_default = True

        if needs_shipping or needs_shipped_at or needs_confirmed_at or needs_status_default:
            logger.info("检测到 orders 表缺少新列，开始补全发货/收货字段。")
            with engine.begin() as connection:
                if needs_shipping:
                    connection.execute(text("ALTER TABLE orders ADD COLUMN shipping_remark VARCHAR(255)"))
                if needs_shipped_at:
                    connection.execute(text("ALTER TABLE orders ADD COLUMN shipped_at DATETIME"))
                if needs_confirmed_at:
                    connection.execute(text("ALTER TABLE orders ADD COLUMN confirmed_at DATETIME"))
                # 将旧状态 created 视为 pending
                if "status" in order_columns:
                    connection.execute(text("UPDATE orders SET status='pending' WHERE status='created'"))
            logger.info("orders 表结构迁移完成。")
