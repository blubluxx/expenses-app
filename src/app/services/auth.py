from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import User
from app.schemas.common.messages import MessageResponse
from app.services.utils.processors import process_db_transaction
from app.services.utils.validators import unique_username, unique_email
from app.schemas.common.application_error import ApplicationError


async def register(user: User, db: AsyncSession):
    """
    Register a new user.

    Args:
        user (User): The user to register.
        db (AsyncSession): The database session.

    Returns:
        Any: The result of the database transaction.
    """

    async def _register():
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

        new_user = User(**user.model_dump())
        db.add(new_user)
        await db.commit()
        db.refresh(new_user)
        return MessageResponse(message="User registered successfully")

    return await process_db_transaction(
        transaction_func=_register,
        db=db,
    )
