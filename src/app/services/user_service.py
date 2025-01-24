import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.user import UserRegistration, UserResponse
from app.schemas.common.common import ResponseMessage
from app.schemas.common.application_error import ApplicationError
from app.services.utils import processors as p, validators as v, utils as u
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)


async def signup(user: UserRegistration, db: AsyncSession) -> ResponseMessage:
    """
    Register a new user.

    Args:
        user (UserRegistration): The user to register.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.
    """

    async def _signup():
        await _validate_data(user=user, db=db)
        hashed_password = u.hash_password(password=user.password)
        user_timezone = _get_user_timezone(user=user)
        new_user = User(
            **user.model_dump(
                exclude={
                    "password",
                    "created_at",
                    "city",
                    "state",
                    "country",
                }
            ),
            password=hashed_password,
            timezone=user_timezone.zone,
        )
        logger.info(f"Registering user: {new_user.id}")
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return ResponseMessage(message="User registered successfully")

    return await p.process_db_transaction(
        transaction_func=_signup,
        db=db,
    )


async def _validate_data(user: UserRegistration, db: AsyncSession) -> None:
    """
    Validate if user username and email are unique.

    Args:
        user (UserRegistration): The user to validate.
        db (AsyncSession): The database session.

    Raises:
        ApplicationError: If the username or email already exists.
    """
    if not await v.unique_username(user.username, db):
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if not await v.unique_email(user.email, db):
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )


def _get_user_timezone(user: UserRegistration) -> Any:
    """
    Get the timezone of a user.

    Args:
        user (UserResponse): The user.

    Returns:
        Any: The timezone of the user.
    """
    timezone: Optional[str] = u.get_timezone(
        city=user.city, country=user.country, state=user.state
    )
    if not timezone:
        timezone = "UTC"
    return timezone


async def get_by_username(username: str, db: AsyncSession) -> UserResponse:
    """
    Get a user by username.

    Args:
        username (str): The username to get.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: DTO representing the User entity.

    Raises:
        ApplicationError: If the user is not found.
    """

    result = await db.execute(select(User).filter(User.username == username))
    user: Optional[User] = result.scalars().first()

    if user is None:
        logger.error(msg=f"No user with username {username} found")

        raise ApplicationError(
            detail=f"No user with username {username} found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.info(msg="Fetched user")
    return UserResponse.create(user=user)


async def get_by_id(user_id: UUID, db: AsyncSession) -> UserResponse:
    """
    Get a user by their ID.

    Args:
        user_id (UUID): The username to get.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: DTO representing the User entity.

    Raises:
        ApplicationError: If the user is not found.
    """

    user: Optional[User] = await _get_db_user_by_id(user_id=user_id, db=db)

    if user is None:
        logger.error(msg=f"No user with user_id {user_id} found")

        raise ApplicationError(
            detail=f"No user with user_id {user_id} found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.info(msg="Fetched user")
    return UserResponse.create(user=user)


async def get_all(
    db: AsyncSession, offset: int = 0, limit: int = 10
) -> list[UserResponse]:
    """
    Returns a list of all users in the database.

    Args:
        db (AsyncSession): The database session.
        offset (int): The offset.
        limit (int): The limit.

    Returns:
        list[UserResponse]: A list of all users in the database.
    """

    result = await db.execute(select(User).offset(offset).limit(limit))
    users: list[User] = result.scalars().all() or []  # type: ignore
    logger.info(msg="Fetched all users")
    return [UserResponse.create(user=user) for user in users]


async def change_user_role(user_id: UUID, db: AsyncSession) -> ResponseMessage:
    """
    Change a user's role.

    Args:
        user_id (UUID): The user's ID.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.

    Raises:
        ApplicationError: If the user is not found.
    """

    async def _change_user_role():
        user: Optional[User] = await _get_db_user_by_id(user_id=user_id, db=db)
        if user is None:
            raise ApplicationError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.is_admin = not user.is_admin
        logger.info(f"Changing is_admin for user {user.id} to {user.is_admin}")
        await db.commit()

        return ResponseMessage(message="User role updated successfully")

    return await p.process_db_transaction(
        transaction_func=_change_user_role,
        db=db,
    )


async def _get_db_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[User]:
    """
    Fetches a User entity from the database.

    Args:
        user_id (UUID): The user's ID.
        db (AsyncSession): The database session.

    Returns:
        User | None: The User entity or None.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user: Optional[User] = result.scalars().first()
    logger.info(f"Fetched user: {user.id if user else None}")
    return user
