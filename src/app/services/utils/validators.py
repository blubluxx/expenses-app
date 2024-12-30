from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import User


async def unique_username(username: str, db: AsyncSession) -> bool:
    """
    Check if a username is unique.

    Args:
        username (str): The username to check.
        db (AsyncSession): The database session.

    Returns:
        bool: True if the username is unique, False otherwise.
    """
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    return user is None
