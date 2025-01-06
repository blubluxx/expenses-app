from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserProfile
from app.schemas.common.messages import ResponseMessage
from app.services.utils import processors as p, validators as v, utils as u
from app.schemas.common.application_error import ApplicationError


async def signup(user: UserProfile, db: AsyncSession) -> ResponseMessage:
    """
    Register a new user.

    Args:
        user (User): The user to register.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.
    """

    async def _signup():
        if not await v.unique_username(user.username, db):
            raise ApplicationError(
                status=409,
                detail="Username already exists",
            )

        if not await v.unique_email(user.email, db):
            raise ApplicationError(
                status=409,
                detail="Email already exists",
            )

        hashed_password = u.hash_password(password=user.password)
        new_user = UserProfile(**user.model_dump(), exclude={"password"})
        new_user.password = hashed_password

        db.add(new_user)
        await db.commit()

        db.refresh(new_user)

        return ResponseMessage(message="User registered successfully")

    return await p.process_db_transaction(
        transaction_func=_signup,
        db=db,
    )
