import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.expense import ExpenseResponse
from app.services.utils import validators as v, utils as u
from app.schemas.common.application_error import ApplicationError
from app.sql_app.expense.expense import Expense
from app.sql_app.expense_name.expense_name import ExpenseName

logger = logging.getLogger(__name__)


async def get_user_expenses(user_id: UUID, db: AsyncSession) -> list[ExpenseResponse]:
    """
    Get all expenses for a user.

    Args:
        user_id (UUID): The user's unique identifier.
        db (AsyncSession): The database session.

    Returns:
        List[ExpenseResponse]: A list of expenses for the user.
    """
    if not await v.user_exists(user_id=user_id, db=db):
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user_expenses = await db.execute(select(Expense).filter(Expense.user_id == user_id))
    expenses = user_expenses.scalars().all()

    return [
        ExpenseName(
            id=expense.id,
            name=expense.name,
            amount=expense.amount,
            date=expense.date,
            created_at=expense.created_at,
        )
        for expense in expenses
    ]
