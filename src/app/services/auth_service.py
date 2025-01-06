from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.sql_app.user.user import User
from app.schemas.user import UserLogin, UserProfile
from app.schemas.common.messages import ResponseMessage
from app.services.utils import utils as u, validators as v, processors as p
from app.schemas.common.application_error import ApplicationError


async def login(
    user: UserLogin,
    db: AsyncSession,
):
    """
    Login a user.

    Args:
        user (UserLogin): The user to login.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.

    Raises:
        ApplicationError: If the user is not found or if the password is wrong.
    """
    pass


def _get_user_by_username(username: str, db: AsyncSession) -> User:
    """
    Get a user by username.

    Args:
        username (str): The username to get.
        db (AsyncSession): The database session.

    Returns:
        User: The user instance.

    Raises:
        ApplicationError: If the user is not found.
    """

    user = (
        db.execute(select(UserProfile).filter(UserProfile.username == username))
        .scalars()
        .first()
    )

    return user


def _authenticate_user(user: UserLogin, db: AsyncSession) -> User:
    """
    Authenticate a user.

    Args:
        user (UserLogin): The user to authenticate.
        db (AsyncSession): The database session.

    Returns:
        User: The user instance.

    Raises:
        ApplicationError: If the user is not found or if the password is wrong.
    """

    user_db = _get_user_by_username(username=user.username, db=db)
    if user_db is None:
        raise ApplicationError(
            status=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    stored_password = user_db.password
    if not u.verify_password(password=user.password, hashed_password=stored_password):
        raise ApplicationError(
            status=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    return user_db
