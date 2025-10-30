from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base


class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=True)
    is_superuser: bool = Column(Boolean, default=False)

