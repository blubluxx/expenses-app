import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.common.application_error import ApplicationError
from app.schemas.user import BaseUser, UpdateUser, UserRegistration, UserResponse
from app.schemas.common.common import ResponseMessage
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
        await _validate_data(
            user_data=BaseUser(username=user.username, email=user.email), db=db
        )
        hashed_password = u.hash_password(password=user.password)
        user_timezone = _get_user_timezone(user=user)
        new_user: UserResponse = await create_new_user(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            timezone=user_timezone,
            db=db,
        )

        return ResponseMessage(
            message=f"User {new_user.username} registered successfully"
        )

    return await p.process_db_transaction(
        transaction_func=_signup,
        db=db,
    )


async def create_new_user(
    username: str,
    email: str,
    hashed_password: str,
    timezone: str,
    db: AsyncSession,
    google_id: str | None = None,
) -> UserResponse:
    """
    Create a new user in the database.

    Args:
        user (UserRegistration): The user to create.
        hashed_password (str): The hashed password of the user.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The created user.
    """

    async def _create():
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            timezone=timezone,
            google_id=google_id,
        )
        logger.info(f"Created user: {new_user.id}")
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse.create(user=new_user)

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def verify_user(user_data: BaseUser, db: AsyncSession) -> ResponseMessage:
    """
    Verify if user data is unique in the database.

    Args:
        user_data (BaseUser): The user data to verify.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.
    """

    await _validate_data(user_data=user_data, db=db)
    return ResponseMessage(message="User data is unique")


async def _validate_data(user_data: BaseUser, db: AsyncSession) -> None:
    """
    Validate if user username and email are unique.

    Args:
        user (UserRegistration): The user to validate.
        db (AsyncSession): The database session.

    Raises:
        ApplicationError: If the username or email already exists.
    """
    if not await v.unique_username(user_data.username, db):
        raise ApplicationError(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if not await v.unique_email(user_data.email, db):
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


async def get_by_google_id(google_id: str, db: AsyncSession) -> Optional[UserResponse]:
    """
    Get a user by Google ID.

    Args:
        google_id (str): The Google ID to get.
        db (AsyncSession): The database session.

    Returns:
        UserResponse | None: DTO representing the User entity or None.

    Raises:
        ApplicationError: If the user is not found.
    """

    result = await db.execute(select(User).filter(User.google_id == google_id))
    user: Optional[User] = result.scalars().first()

    logger.info(msg=f"Fetched user with google_id {google_id}")
    return UserResponse.create(user=user) if user else None


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


async def update_user(
    user: UserResponse, update_data: UpdateUser, db: AsyncSession
) -> UserResponse:
    """
    Updates the User entity.

    Args:
        user (UserResponse): The current logged in User.
        update_data (UpdateUser): The Pydantic model for User update.
        db (AsyncSession): The database dependency.

    Returns:
        UserResponse: The updated User.
    """

    user: User = _get_db_user_by_id(user_id=user.id)
    if user is None:
        raise ApplicationError(
            detail=f"User with ID {user.id} not found",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return await _update_user(user=user, update_data=update_data, db=db)


async def _update_user(
    user: User, update_data: UpdateUser, db: AsyncSession
) -> UserResponse:
    """
    Updates the User entity.

    Args:
        user (User): The User entity.
        update_data (UpdateUser): The Pydantic model for User update.
        db (AsyncSession): The database dependency.

    Returns:
        UserResponse: DTO for the updated User entity.
    """

    async def _update():
        if update_data.username is not None and v.unique_username(
            username=update_data.username, db=db
        ):
            user.username = update_data.username
        if update_data.email is not None and v.unique_email(
            email=update_data.email, db=db
        ):
            user.email = update_data.email
        if update_data.timezone is not None:
            user.timezone = update_data.timezone
        if update_data.password:
            hashed_password = u.hash_password(password=update_data.password)
            if hashed_password == user.password:
                raise ApplicationError(
                    detail="New password must be different from the old password",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            user.password = hashed_password

        await db.commit()
        await db.refresh(user)
        logger.info(f"Updated user info for user with ID {user.id}")
        return UserResponse.create(user=user)

    return await p.process_db_transaction(transaction_func=_update, db=db)
