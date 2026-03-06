"""互动领域接口。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.localization.messages import MESSAGES
from app.models.post import Post
from app.models.user import User
from app.schemas.common import PaginationMeta, ResponseModel
from app.schemas.post import CommentCreate, CommentRead, PostCreate, PostRead, PostUpdate, ReactionRequest
from app.services.audit_service import AuditService
from app.services.post_service import PostService, ReactionService
from app.utils.exceptions import BusinessException
from app.utils.request import extract_client_ip

router = APIRouter(prefix="/posts", tags=["互动"])


@router.post("/", response_model=ResponseModel[PostRead])
def create_post(
    payload: PostCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[PostRead]:
    """创建帖子。"""

    post = PostService(db).create_post(payload, current_user.id)
    AuditService(db).record(
        actor_id=current_user.id,
        action="create_post",
        target_type="post",
        target_id=str(post.id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["post_created"], data=_post_to_read(post))


@router.get("/", response_model=ResponseModel[list[PostRead]])
def list_posts(
    status_filter: Optional[str] = Query(None, alias="status"),
    topic: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[PostRead]]:
    """分页查询帖子。"""

    posts, total = PostService(db).list_posts(
        status=status_filter,
        topic=topic,
        page=page,
        page_size=page_size,
        current_user_role=current_user.role,
        current_user_id=current_user.id,
    )
    return ResponseModel(
        code=0,
        message=MESSAGES["post_list"],
        data=[_post_to_read(post) for post in posts],
        meta=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.patch(
    "/{post_id}",
    dependencies=[Depends(require_roles("admin", "practitioner"))],
    response_model=ResponseModel[PostRead],
)
def update_post(
    post_id: int,
    payload: PostUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[PostRead]:
    """更新帖子内容或状态。"""

    service = PostService(db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    if current_user.role != "admin" and post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MESSAGES["permission_denied"])
    updated = service.update_post(post, payload, reviewer_id=current_user.id if current_user.role == "admin" else None)
    AuditService(db).record(
        actor_id=current_user.id,
        action="update_post",
        target_type="post",
        target_id=str(post_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["post_updated"], data=_post_to_read(updated))


@router.post(
    "/{post_id}/comments",
    response_model=ResponseModel[CommentRead],
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[CommentRead]:
    """在帖子下创建评论。"""

    service = PostService(db)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or post.status not in {"approved", "pending", "draft"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在或不可评论")
    comment = service.create_comment(post, payload, current_user.id)
    AuditService(db).record(
        actor_id=current_user.id,
        action="create_comment",
        target_type="post",
        target_id=str(post_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["comment_created"], data=CommentRead.from_orm(comment))


@router.get(
    "/{post_id}/comments",
    response_model=ResponseModel[list[CommentRead]],
)
def list_comments(
    post_id: int,
    db: Session = Depends(get_db_session),
) -> ResponseModel[list[CommentRead]]:
    """获取帖子下的已审核评论。"""

    service = PostService(db)
    comments = service.list_comments(post_id)
    return ResponseModel(code=0, message=MESSAGES["post_list"], data=[CommentRead.from_orm(item) for item in comments])


@router.post("/reactions", response_model=ResponseModel[None])
def create_reaction(
    payload: ReactionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ResponseModel[None]:
    """执行点赞或收藏。"""

    service = ReactionService(db)
    try:
        reaction = service.toggle(current_user.id, payload.target_type, payload.target_id, payload.reaction_type)
    except BusinessException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    if payload.target_type == "post":
        PostService(db).update_counters(payload.target_id)
    AuditService(db).record(
        actor_id=current_user.id,
        action=f"reaction_{payload.reaction_type}",
        target_type=payload.target_type,
        target_id=str(payload.target_id),
        note=payload.json(exclude_none=True, ensure_ascii=False),
        ip=extract_client_ip(request),
    )
    return ResponseModel(code=0, message=MESSAGES["reaction_success"], data=None)


def _post_to_read(post: Post) -> PostRead:
    """将 ORM 转换为响应模型。"""

    return PostRead(
        id=post.id,
        title=post.title,
        content_md=post.content_md,
        topic=post.topic,
        status=post.status,
        like_count=post.like_count,
        favorite_count=post.favorite_count,
        author_id=post.author_id,
        reviewer_id=post.reviewer_id,
        review_note=post.review_note,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )
