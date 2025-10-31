from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from app.schemas.auth import Token
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_active_user


router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Registers a new user in the system.
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


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticates a user and returns an access token upon successful login.
    """
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Retrieves the current authenticated user's information.
    """
    return current_user
