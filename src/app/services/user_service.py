from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserSignup
from app.schemas.common.messages import ResponseMessage
from app.services.utils.processors import process_db_transaction
from app.services.utils.validators import unique_username, unique_email
from app.schemas.common.application_error import ApplicationError


async def signup(user: UserSignup, db: AsyncSession) -> ResponseMessage:
    """
    Register a new user.

    Args:
        user (User): The user to register.
        db (AsyncSession): The database session.

    Returns:
        ResponseMessage: The response message.
    """

    async def _signup():
        if not unique_username(user.username, db):
            raise ApplicationError(
                status=409,
                detail="Username already exists",
            )

        if not unique_email(user.email, db):
            raise ApplicationError(
                status=409,
                detail="Email already exists",
            )

        new_user = UserSignup(**user.model_dump())
        db.add(new_user)
        await db.commit()
        db.refresh(new_user)
        return ResponseMessage(message="User registered successfully")

    return await process_db_transaction(
        transaction_func=_signup,
        db=db,
    )
