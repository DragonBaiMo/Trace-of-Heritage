"""个性化推荐接口。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.localization.messages import MESSAGES
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.resource import ResourceRead
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["推荐"])


@router.get("/", response_model=ResponseModel[list[ResourceRead]])
def recommend_resources(
    limit: int = Query(6, ge=1, le=20, description="返回的推荐数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[ResourceRead]]:
    """为当前用户返回个性化推荐资源。"""

    resources = RecommendationService(db).recommend_resources(current_user.id, limit=limit)
    return ResponseModel(
        code=0,
        message=MESSAGES["recommendation_loaded"],
        data=[
            ResourceRead(
                id=item.id,
                title=item.title,
                resource_type=item.resource_type,
                synopsis=item.synopsis,
                tags=item.tags or [],
                era=item.era,
                genre=item.genre,
                region_code=item.region_code,
                author=item.author,
                copyright_status=item.copyright_status,
                status=item.status,
                file_path=item.file_path,
                external_url=item.external_url,
                submitter_id=item.submitter_id,
                reviewer_id=item.reviewer_id,
                review_note=item.review_note,
                created_at=item.created_at,
                updated_at=item.updated_at,
                trails=[],
            )
            for item in resources
        ],
    )
