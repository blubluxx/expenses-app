import logging

import pandas as pd

from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common.enum import TimePeriod
from app.services.utils import processors as p
from app.services.expense_service import filter_by_time_period
from app.sql_app.expense.expense import Expense

logger = logging.getLogger(__name__)


async def analyze_expenses(
    user_id: int, time_period: TimePeriod, db: AsyncSession
) -> JSONResponse:
    """
    Get the total expenses for a user in a given time period.

    Args:
        user_id (int): The user ID.
        time_period (TimePeriod): The time period.
        db (AsyncSession): The database session.

    Returns:
        JSONResponse: The total expenses for the user in the given time period.
    """

    async def _analyze_expenses():
        query = select(Expense).filter(
            Expense.user_id == user_id, Expense.is_deleted == False
        )
        query = await filter_by_time_period(query=query, time_period=time_period)
        result = await db.execute(query)
        expenses: list[Expense] = result.scalars().unique()

        expense_data = [
            {
                "date": expense.date,
                "amount": float(expense.amount),
                "category": expense.name.category.name,
            }
            for expense in expenses
        ]
        df = pd.DataFrame(expense_data)

        if df.empty:
            return {"total_expenses": []}

        category_expenses = df.groupby("category")["amount"].sum().reset_index()

        category_expenses = category_expenses.to_dict(orient="records")
        return {"total_expenses": category_expenses}

    return await p.process_db_transaction(
        transaction_func=_analyze_expenses,
        db=db,
    )
