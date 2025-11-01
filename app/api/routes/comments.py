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
from app.core.security import get_current_active_user

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
    # Verify post exists and is not deleted
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
    return db_comment


@router.get("/", response_model=List[CommentInDB])
async def read_comments(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    post_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100  # Default limit for non-paginated list
):
    """
    Retrieves a list of all comments, optionally filtered by post_id. Requires authentication.
    Includes owner data.
    """
    query = (
        select(Comment)
        .options(selectinload(Comment.owner))
        .filter(Comment.is_deleted == False)
    )
    if post_id:
        query = query.filter(Comment.post_id == post_id)

    result = await db.execute(
        query.offset(skip).limit(limit)  # Manual limit/offset for now
    )
    # .unique() needed when loading collections
    comments = result.scalars().unique().all()
    return comments


@router.get("/{comment_id}", response_model=CommentInDB)
async def read_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves a specific comment by ID. Requires authentication.
    Includes owner data.
    """
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .filter(Comment.id == comment_id, Comment.is_deleted == False)
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
    return db_comment


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
