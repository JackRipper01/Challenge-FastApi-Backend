from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload  # For eagerly loading relationships

from app.db.session import get_async_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostInDB
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=PostInDB, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new post. Requires authentication.
    The current authenticated user will be set as the owner.
    """
    db_post = Post(**post_in.model_dump(), owner_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.owner), selectinload(Post.comments))
        .filter(Post.id == db_post.id)
    )
    fully_loaded_post = result.scalar_one()
    return fully_loaded_post

@router.get("/", response_model=List[PostInDB])
async def read_posts(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100  # Default limit for non-paginated list
):
    """
    Retrieves a list of all posts. Requires authentication.
    Includes owner and comments data.
    """
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.owner), selectinload(Post.comments))
        .filter(Post.is_deleted == False)
        .offset(skip).limit(limit)  # Manual limit/offset for now
    )
    # .unique() needed when loading collections
    posts = result.scalars().unique().all()
    return posts


@router.get("/{post_id}", response_model=PostInDB)
async def read_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves a specific post by ID. Requires authentication.
    Includes owner and comments data.
    """
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.owner), selectinload(Post.comments))
        .filter(Post.id == post_id, Post.is_deleted == False)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post


@router.put("/{post_id}", response_model=PostInDB)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates an existing post. Requires authentication and ownership.
    """
    result = await db.execute(
        select(Post)
        .filter(Post.id == post_id, Post.is_deleted == False)
    )
    db_post = result.scalar_one_or_none()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this post.")

    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft-deletes a post. Requires authentication and ownership.
    """
    result = await db.execute(
        select(Post)
        .filter(Post.id == post_id, Post.is_deleted == False)
    )
    db_post = result.scalar_one_or_none()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this post.")

    db_post.is_deleted = True
    db.add(db_post)
    await db.commit()
    return
