from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_async_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentInDB
from app.core.security import get_current_active_user, get_current_active_superuser
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter()


@router.post("/", response_model=CommentInDB, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new comment on a post. Requires authentication.
    The current authenticated user will be set as the owner.
    """
    post_result = await db.execute(
        select(Post).filter(Post.id == comment_in.post_id,
                            Post.is_deleted == False)
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    db_comment = Comment(
        **comment_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    # Re-query to eagerly load owner for response
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .filter(Comment.id == db_comment.id)
    )
    fully_loaded_comment = result.scalar_one()
    return fully_loaded_comment


@router.get("/", response_model=PaginatedResponse[CommentInDB])
async def read_comments(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    post_id: Optional[int] = None,
    include_deleted: bool = False,
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieves a paginated list of all comments, optionally filtered by post_id.
    By default, only non-deleted comments are returned. Superusers can
    set 'include_deleted=true' to see all comments.
    """
    query = (
        select(Comment)
        .options(selectinload(Comment.owner))
    )

    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted comments."
        )

    if not include_deleted:
        query = query.filter(Comment.is_deleted == False)

    if post_id:
        query = query.filter(Comment.post_id == post_id)

    return await paginate(db, query, skip, limit)


@router.get("/{comment_id}", response_model=CommentInDB)
async def read_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    include_deleted: bool = False
):
    """
    Retrieves a specific comment by ID. Requires authentication.
    By default, only non-deleted comments are returned. Superusers can
    set 'include_deleted=true' to retrieve a deleted comment.
    """
    query = select(Comment).options(selectinload(Comment.owner))

    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted comments."
        )

    if not include_deleted:
        query = query.filter(Comment.is_deleted == False)

    result = await db.execute(
        query.filter(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    return comment


@router.put("/{comment_id}", response_model=CommentInDB)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates an existing comment. Requires authentication and ownership.
    """
    result = await db.execute(
        select(Comment)
        .filter(Comment.id == comment_id, Comment.is_deleted == False)
    )
    db_comment = result.scalar_one_or_none()
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this comment.")

    update_data = comment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_comment, field, value)

    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    # Re-query to eagerly load owner for response
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .filter(Comment.id == db_comment.id)
    )
    fully_loaded_comment = result.scalar_one()
    return fully_loaded_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft-deletes a comment. Requires authentication and ownership.
    """
    result = await db.execute(
        select(Comment)
        .filter(Comment.id == comment_id, Comment.is_deleted == False)
    )
    db_comment = result.scalar_one_or_none()
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this comment.")

    db_comment.is_deleted = True
    db.add(db_comment)
    await db.commit()
    return
