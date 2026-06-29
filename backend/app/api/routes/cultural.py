"""文化分享接口：视频推荐 + 每周荐读。"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.common import PaginationMeta, ResponseModel
from app.schemas.cultural import VideoRecommendationRead, WeeklyDigestRead
from app.services.cultural_service import CulturalService

router = APIRouter(prefix="/cultural", tags=["文化分享"])


@router.get("/videos", response_model=ResponseModel[List[VideoRecommendationRead]])
def list_videos(
    genre: Optional[str] = Query(None, description="戏曲类型筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> ResponseModel[List[VideoRecommendationRead]]:
    svc = CulturalService(db)
    items, total = svc.list_videos(genre=genre, page=page, page_size=page_size)
    return ResponseModel(
        code=0,
        message="ok",
        data=[VideoRecommendationRead.from_orm(x) for x in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/weekly", response_model=ResponseModel[List[WeeklyDigestRead]])
def list_digests(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db_session),
) -> ResponseModel[List[WeeklyDigestRead]]:
    svc = CulturalService(db)
    items, total = svc.list_digests(page=page, page_size=page_size)
    return ResponseModel(
        code=0,
        message="ok",
        data=[WeeklyDigestRead.from_orm(x) for x in items],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/weekly/latest", response_model=ResponseModel[Optional[WeeklyDigestRead]])
def get_latest_digest(db: Session = Depends(get_db_session)) -> ResponseModel[Optional[WeeklyDigestRead]]:
    svc = CulturalService(db)
    digest = svc.get_latest_digest()
    data = WeeklyDigestRead.from_orm(digest) if digest else None
    return ResponseModel(code=0, message="ok", data=data)
