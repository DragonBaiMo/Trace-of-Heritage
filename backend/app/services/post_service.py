"""帖子与互动服务。"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.localization.messages import MESSAGES
from app.models.post import Comment, Post, Reaction
from app.schemas.post import CommentCreate, PostCreate, PostUpdate
from app.utils.exceptions import BusinessException


class PostService:
    """封装帖子与评论的业务逻辑。"""

    def __init__(self, db: Session):
        self.db = db

    def create_post(self, payload: PostCreate, author_id: int) -> Post:
        """创建帖子并根据意图设置状态。"""

        post = Post(
            title=payload.title,
            content_md=payload.content_md,
            topic=payload.topic,
            status="pending" if payload.submit_for_review else "draft",
            author_id=author_id,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update_post(self, post: Post, payload: PostUpdate, reviewer_id: Optional[int] = None) -> Post:
        """更新帖子。"""

        data = payload.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(post, field, value)
        if reviewer_id:
            post.reviewer_id = reviewer_id
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def review_post(self, post: Post, decision: str, review_note: Optional[str], reviewer_id: int) -> Post:
        """审核帖子。"""

        if post.status not in {"pending", "draft"}:
            raise BusinessException(MESSAGES["resource_invalid_state"])
        if decision == "reject" and (not review_note or len(review_note.strip()) < 5):
            raise BusinessException(MESSAGES["review_note_required"])
        post.status = "approved" if decision == "approve" else "rejected"
        post.review_note = review_note
        post.reviewer_id = reviewer_id
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def list_posts(
        self,
        *,
        status: Optional[str] = None,
        topic: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_role: str,
        current_user_id: int,
    ) -> tuple[list[Post], int]:
        """分页查询帖子。"""

        query = self.db.query(Post)
        if status:
            query = query.filter(Post.status == status)
        if topic:
            query = query.filter(Post.topic == topic)
        if current_user_role != "admin":
            query = query.filter((Post.status == "approved") | (Post.author_id == current_user_id))
        total = query.count()
        items = (
            query.order_by(Post.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create_comment(self, post: Post, payload: CommentCreate, author_id: int) -> Comment:
        """创建评论。"""

        comment = Comment(
            post_id=post.id,
            author_id=author_id,
            content=payload.content,
            status="pending" if post.status != "approved" else "approved",
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(self, post_id: int) -> list[Comment]:
        """列出评论。"""

        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id, Comment.status == "approved")
            .order_by(Comment.created_at.asc())
            .all()
        )

    def update_counters(self, post_id: int) -> None:
        """根据 Reaction 表刷新帖子互动计数。"""

        like_count = (
            self.db.query(func.count(Reaction.id))
            .filter(Reaction.target_type == "post", Reaction.target_id == post_id, Reaction.reaction_type == "like")
            .scalar()
            or 0
        )
        favorite_count = (
            self.db.query(func.count(Reaction.id))
            .filter(
                Reaction.target_type == "post",
                Reaction.target_id == post_id,
                Reaction.reaction_type == "favorite",
            )
            .scalar()
            or 0
        )
        self.db.query(Post).filter(Post.id == post_id).update(
            {Post.like_count: like_count, Post.favorite_count: favorite_count}
        )
        self.db.commit()


class ReactionService:
    """互动行为服务。"""

    def __init__(self, db: Session):
        self.db = db

    def toggle(self, user_id: int, target_type: str, target_id: int, reaction_type: str) -> Reaction:
        """创建互动，若重复则抛出业务异常。"""

        existing = (
            self.db.query(Reaction)
            .filter(
                Reaction.user_id == user_id,
                Reaction.target_type == target_type,
                Reaction.target_id == target_id,
                Reaction.reaction_type == reaction_type,
            )
            .first()
        )
        if existing:
            raise BusinessException(MESSAGES["reaction_duplicate"], code=40901)
        reaction = Reaction(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            reaction_type=reaction_type,
        )
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        return reaction
