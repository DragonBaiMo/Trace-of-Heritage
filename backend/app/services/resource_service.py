"""资源领域服务，负责资源的增删改查及审核状态管理。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.localization.messages import MESSAGES
from app.models.resource import Resource, ResourceGeoTrail
from app.schemas.resource import ResourceCreate, ResourceTrailCreate, ResourceUpdate
from app.utils.exceptions import BusinessException


class ResourceService:
    """资源服务封装数据库操作，确保规则集中管理。"""

    def __init__(self, db: Session):
        self.db = db

    def create_resource(self, payload: ResourceCreate, creator_id: int) -> tuple[Resource, str | None]:
        """创建新的资源并根据意图设置状态，返回资源与水印提示。"""

        resource = Resource(
            title=payload.title,
            resource_type=payload.resource_type,
            file_path=payload.file_path,
            external_url=payload.external_url,
            synopsis=payload.synopsis,
            tags=payload.tags,
            era=payload.era,
            genre=payload.genre,
            region_code=payload.region_code,
            author=payload.author,
            copyright_status=payload.copyright_status,
            status="pending" if payload.submit_for_review else "draft",
            submitter_id=creator_id,
        )
        self.db.add(resource)
        self.db.flush()
        if payload.trails:
            self._replace_trails(resource, payload.trails)
        watermark_warning = self._apply_watermark_if_needed(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource, watermark_warning

    def list_resources(
        self,
        *,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_role: str = "user",
        current_user_id: Optional[int] = None,
    ) -> tuple[list[Resource], int]:
        """按状态与关键词筛选资源，并返回分页数据与总数。"""

        query = self.db.query(Resource)
        if status:
            query = query.filter(Resource.status == status)
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                or_(Resource.title.ilike(like_pattern), Resource.synopsis.ilike(like_pattern))
            )
        if current_user_role != "admin":
            query = query.filter(
                or_(Resource.status == "approved", Resource.submitter_id == current_user_id)
            )
        total = query.count()
        items = (
            query.order_by(Resource.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_resource(self, resource_id: int) -> Optional[Resource]:
        """根据主键获取资源。"""

        return self.db.query(Resource).filter(Resource.id == resource_id).first()

    def update_resource(self, resource: Resource, payload: ResourceUpdate, *, reviewer_id: Optional[int] = None) -> tuple[Resource, str | None]:
        """更新资源信息，同时保留审计字段，返回可能的水印提示。"""

        data = payload.dict(exclude_unset=True)
        watermark_warning: str | None = None
        if trails := data.pop("trails", None):
            normalized = [
                trail if isinstance(trail, ResourceTrailCreate) else ResourceTrailCreate(**trail)
                for trail in trails
            ]
            self._replace_trails(resource, normalized)
        file_path_changed = "file_path" in data and data.get("file_path") != resource.file_path
        for field, value in data.items():
            setattr(resource, field, value)
        if reviewer_id:
            resource.reviewer_id = reviewer_id
        if file_path_changed:
            watermark_warning = self._apply_watermark_if_needed(resource)
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource, watermark_warning

    def review_resource(self, resource: Resource, decision: str, review_note: Optional[str], reviewer_id: int) -> Resource:
        """管理员审核资源。"""

        if resource.status not in {"pending", "draft"}:
            raise BusinessException(MESSAGES["resource_invalid_state"])
        if decision == "reject" and (not review_note or len(review_note.strip()) < 5):
            raise BusinessException(MESSAGES["review_note_required"])
        resource.status = "approved" if decision == "approve" else "rejected"
        resource.review_note = review_note
        resource.reviewer_id = reviewer_id
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def summarize(self) -> dict[str, int | list[Resource]]:
        """统计资源状态数量并返回最近记录。"""

        status_counts = {
            status: count
            for status, count in self.db.query(Resource.status, func.count(Resource.id))
            .group_by(Resource.status)
            .all()
        }
        latest = (
            self.db.query(Resource)
            .order_by(Resource.updated_at.desc())
            .limit(5)
            .all()
        )
        total = sum(status_counts.values()) if status_counts else 0
        return {
            "total": total,
            "pending": status_counts.get("pending", 0),
            "approved": status_counts.get("approved", 0),
            "rejected": status_counts.get("rejected", 0),
            "latest": latest,
        }

    def list_trails(self, resource_id: int) -> list[ResourceGeoTrail]:
        """按顺序返回轨迹点，资源不存在时抛出业务异常。"""

        resource = self.get_resource(resource_id)
        if not resource:
            raise BusinessException(MESSAGES["resource_not_found"])
        return sorted(resource.trails, key=lambda item: item.order_no)

    def _replace_trails(self, resource: Resource, trails: Sequence[ResourceTrailCreate]) -> None:
        """重置资源的轨迹点。"""

        resource.trails.clear()
        for trail in sorted(trails, key=lambda item: item.order_no):
            resource.trails.append(
                ResourceGeoTrail(
                    place_name=trail.place_name,
                    region_code=trail.region_code,
                    longitude=trail.longitude,
                    latitude=trail.latitude,
                    occurred_at=trail.occurred_at,
                    order_no=trail.order_no,
                )
            )

    def _apply_watermark_if_needed(self, resource: Resource) -> str | None:
        """对图片类资源添加文字水印，失败时返回提示文本。"""

        file_path = resource.file_path
        if not file_path:
            return None
        suffix = file_path.lower()
        if not suffix.endswith((".png", ".jpg", ".jpeg", ".webp")):
            return None

        target_path = Path(file_path)
        base_dir = Path(settings.media_root)
        is_relative = not target_path.is_absolute()
        if is_relative:
            target_path = base_dir / file_path.lstrip("/\\")
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if not target_path.exists():
            return "未找到原始文件，已跳过水印处理"

        try:
            image = Image.open(target_path).convert("RGBA")
            txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            text = f"{resource.title}-{resource.author or '佚名'}"
            font = ImageFont.load_default()
            text_width, text_height = draw.textsize(text, font=font)
            padding = 10
            position = (image.width - text_width - padding, image.height - text_height - padding)
            draw.text(position, text, fill=(255, 255, 255, 140), font=font)
            watermarked = Image.alpha_composite(image, txt_layer)
            output_path = target_path.with_name(f"{target_path.stem}_wm{target_path.suffix}")
            watermarked.convert("RGB").save(output_path)
            if is_relative and output_path.is_relative_to(base_dir):
                relative_path = output_path.relative_to(base_dir)
                resource.file_path = str(relative_path).replace("\\", "/")
            else:
                resource.file_path = str(output_path)
            return None
        except Exception as exc:  # 捕获 Pillow 处理异常，返回中文提示不中断主流程
            return f"水印处理失败：{exc}"
