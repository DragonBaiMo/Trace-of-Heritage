"""审计日志服务，统一写入操作记录。"""
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


class AuditService:
    """负责将重要操作持久化到审计日志表中。"""

    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        actor_id: int,
        action: str,
        target_type: str,
        target_id: str,
        *,
        note: str | None = None,
        ip: str | None = None,
    ) -> AuditLog:
        """写入审计日志，将备注与客户端 IP 一并记录。"""

        log = AuditLog(actor_id=actor_id, action=action, target_type=target_type, target_id=target_id, note=note, ip=ip)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, limit: int = 50) -> Iterable[AuditLog]:
        """按时间倒序返回日志记录，可配置最大条数。"""

        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
