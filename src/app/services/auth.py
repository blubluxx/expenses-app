from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import User
from app.services.utils.processors import process_db_transaction
from app.services.utils.validators import unique_username
from app.schemas.exceptions.application_error import ApplicationError


async def register(user: User, db: AsyncSession):
    """
    Register a new user.

    Args:
        user (User): The user to register.
        db (AsyncSession): The database session.

    Returns:
        Any: The result of the database transaction.
    """

    def _register():
        pass

    return await process_db_transaction(
        transaction_func=_register,
        db=db,
    )
