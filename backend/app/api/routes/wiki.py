"""百科接口。"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.common import PaginationMeta, ResponseModel
from app.schemas.wiki import WikiEntryRead
from app.services.wiki_service import WikiService

router = APIRouter(prefix="/wiki", tags=["百科"])


@router.get("/entries", response_model=ResponseModel[list[WikiEntryRead]])
def list_entries(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[WikiEntryRead]]:
    service = WikiService(db)
    items, total = service.list_entries(keyword=keyword, category=category, page=page, page_size=page_size)
    return ResponseModel(code=0, message="ok", data=[WikiEntryRead.from_orm(x) for x in items], meta=PaginationMeta(page=page, page_size=page_size, total=total))


@router.get("/entries/{entry_id}", response_model=ResponseModel[WikiEntryRead])
def get_entry(entry_id: int, db: Session = Depends(get_db_session)) -> ResponseModel[WikiEntryRead]:
    service = WikiService(db)
    entry = service.get_entry(entry_id)
    return ResponseModel(code=0, message="ok", data=WikiEntryRead.from_orm(entry))
