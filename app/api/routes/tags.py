from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_async_db
from app.models.tag import Tag
from app.models.post import Post
from app.models.user import User
from app.models.comment import Comment
from app.schemas.tag import TagCreate, TagUpdate, TagInDB
from app.schemas.post import PostInDB
from app.core.security import get_current_active_user, get_current_active_superuser
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter()


@router.post("/", response_model=TagInDB, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Creates a new tag. Requires superuser privileges.
    Checks for uniqueness among non-deleted tags.
    """
    existing_tag = await db.execute(
        select(Tag).filter(Tag.name == tag_in.name, Tag.is_deleted == False)
    )
    if existing_tag.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_in.name}' already exists."
        )

    db_tag = Tag(**tag_in.model_dump())
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


@router.get("/", response_model=PaginatedResponse[TagInDB])
async def read_tags(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False
):
    """
    Retrieves a paginated list of all tags. Requires authentication.
    By default, only non-deleted tags are returned. Superusers can
    set 'include_deleted=true' to see all tags, including soft-deleted ones.
    """
    query = select(Tag)

    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted tags."
        )

    if not include_deleted:
        query = query.filter(Tag.is_deleted == False)

    return await paginate(db, query, skip, limit)


@router.get("/{tag_id}", response_model=TagInDB)
async def read_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    include_deleted: bool = False
):
    """
    Retrieves a specific tag by ID. Requires authentication.
    By default, only non-deleted tags are returned. Superusers can
    set 'include_deleted=true' to retrieve a soft-deleted tag.
    """
    query = select(Tag)

    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted tags."
        )

    if not include_deleted:
        query = query.filter(Tag.is_deleted == False)

    result = await db.execute(
        query.filter(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")
    return tag


@router.put("/{tag_id}", response_model=TagInDB)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Updates an existing tag. Requires superuser privileges.
    """
    result = await db.execute(
        select(Tag)
        .filter(Tag.id == tag_id, Tag.is_deleted == False)
    )
    db_tag = result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    update_data = tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)

    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Soft-deletes a tag. Requires superuser privileges.
    """
    result = await db.execute(
        select(Tag)
        .filter(Tag.id == tag_id, Tag.is_deleted == False)
    )
    db_tag = result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    db_tag.is_deleted = True
    db.add(db_tag)
    await db.commit()
    return


@router.post("/{tag_id}/add_to_post/{post_id}", response_model=PostInDB, status_code=status.HTTP_200_OK)
async def add_tag_to_post(
    tag_id: int,
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Adds a tag to a post. Requires authentication and either ownership of the post OR superuser privileges.
    """
    post_result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .filter(Post.id == post_id, Post.is_deleted == False)
    )
    db_post = post_result.scalar_one_or_none()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if not current_user.is_superuser and db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to modify this post.")

    tag_result = await db.execute(
        select(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False)
    )
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    if db_tag not in db_post.tags:
        db_post.tags.append(db_tag)
        await db.commit()
        await db.refresh(db_post)

    # Re-query the post with all relationships eagerly loaded for the response
    fully_loaded_post_result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.owner),
            selectinload(Post.comments).selectinload(Comment.owner),
            selectinload(Post.tags)
        )
        .filter(Post.id == db_post.id)
    )
    fully_loaded_post = fully_loaded_post_result.scalar_one()
    return fully_loaded_post


@router.post("/{tag_id}/remove_from_post/{post_id}", response_model=PostInDB, status_code=status.HTTP_200_OK)
async def remove_tag_from_post(
    tag_id: int,
    post_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Removes a tag from a post. Requires authentication and either ownership of the post OR superuser privileges.
    """
    post_result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .filter(Post.id == post_id, Post.is_deleted == False)
    )
    db_post = post_result.scalar_one_or_none()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if not current_user.is_superuser and db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to modify this post.")

    tag_result = await db.execute(
        select(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False)
    )
    db_tag = tag_result.scalar_one_or_none()
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    if db_tag in db_post.tags:
        db_post.tags.remove(db_tag)
        await db.commit()
        await db.refresh(db_post)

    # Re-query the post with all relationships eagerly loaded for the response
    fully_loaded_post_result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.owner),
            selectinload(Post.comments).selectinload(Comment.owner),
            selectinload(Post.tags)
        )
        .filter(Post.id == db_post.id)
    )
    fully_loaded_post = fully_loaded_post_result.scalar_one()
    return fully_loaded_post
