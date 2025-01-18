from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.sql_app.user.user import User


async def unique_username(username: str, db: AsyncSession) -> bool:
    """
    Checks if a username is unique.

    Args:
        username (str): The username to check.
        db (AsyncSession): The database session.

    Returns:
        bool: True if the username is unique, False otherwise.
    """
    result = await db.execute(select(User).filter(User.username == username))
    user: Optional[User] = result.scalars().first()
    return user is None


async def unique_email(email: str, db: AsyncSession) -> bool:
    """
    Checks if an email is unique.

    Args:
        email (str): The email to check.
        db (AsyncSession): The database session.

    Returns:
        bool: True if the email is unique, False otherwise.
    """
    result = await db.execute(select(User).filter(User.email == email))
    user: Optional[User] = result.scalars().first()
    return user is None


async def user_exists(user_id: UUID, db: AsyncSession) -> bool:
    """
    Checks if a user exists in the database.

    Args:
        user_id (str): The user_id to check.
        db (AsyncSession): The database session.

    Returns:
        bool: True if the user is unique, False otherwise.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user: Optional[User] = result.scalars().first()
    return user is not None
