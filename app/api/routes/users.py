from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.models.user import User
from app.core.security import get_current_active_superuser, get_password_hash, get_current_active_user
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter()


@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Creates a new user in the system. Requires superuser privileges.
    The password will be hashed before storage.
    """
    existing_user = await db.execute(select(User).filter(User.email == user_in.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=PaginatedResponse[UserInDB])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    # Superusers can list all users
    current_user: User = Depends(get_current_active_superuser),
    include_deleted: bool = False
):
    """
    Retrieves a paginated list of all non-deleted users. Requires superuser privileges.
    Superusers can set 'include_deleted=true' to see all users, including soft-deleted ones.
    """
    query = select(User)

    # Permission check for include_deleted
    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted users."
        )

    # Apply soft-delete filter if not including deleted
    if not include_deleted:
        query = query.filter(User.is_deleted == False)

    return await paginate(db, query, skip, limit)


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    # Superusers can retrieve any user
    current_user: User = Depends(get_current_active_superuser),
    include_deleted: bool = False
):
    """
    Retrieves a specific user by ID. Requires superuser privileges.
    By default, only non-deleted users are retrieved. Superusers can
    set 'include_deleted=true' to retrieve a soft-deleted user.
    """
    query = select(User)

    # Permission check for include_deleted
    if include_deleted and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view deleted users."
        )

    # Apply soft-delete filter if not including deleted
    if not include_deleted:
        query = query.filter(User.is_deleted == False)

    result = await db.execute(
        query.filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Updates an existing user. Requires superuser privileges.
    If a new password is provided, it will be hashed.
    """
    result = await db.execute(
        select(User)
        .filter(User.id == user_id, User.is_deleted == False)
    )
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value is not None:
            db_user.hashed_password = get_password_hash(value)
        else:
            setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Soft-deletes a user from the system by setting 'is_deleted' to True.
    Requires superuser privileges.
    """
    result = await db.execute(
        select(User)
        .filter(User.id == user_id, User.is_deleted == False)
    )
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db_user.is_deleted = True
    db.add(db_user)
    await db.commit()
    return
