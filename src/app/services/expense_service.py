import logging
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.category import CategoryResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseNameDTO
from app.services import category_service
from app.services.utils import validators as v, utils as u, processors as p
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
        logger.error(f"User not found: {user_id}")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user_expenses = await db.execute(select(Expense).filter(Expense.user_id == user_id))
    expenses: list[Expense] = user_expenses.scalars().all() or []  # type: ignore
    logger.info(f"Fetched all expenses for user: {user_id}")

    return [
        ExpenseResponse(
            id=expense.id,
            name=expense.name,  # type: ignore
            amount=expense.amount,
            date=expense.date,
            created_at=expense.created_at,
        )
        for expense in expenses
    ]


async def create_expense(
    user_id: UUID, expense: ExpenseCreate, db: AsyncSession
) -> ExpenseResponse:
    """
    Create an expense.

    Args:
        user_id (UUID): The user's unique identifier.
        expense (ExpenseCreate): The expense to create.
        db (AsyncSession): The database session.

    Returns:
        ExpenseResponse: The created expense.
    """
    category: CategoryResponse = await _validate_data(
        user_id=user_id, category_name=expense.category, db=db
    )

    async def _create():
        expense_name: ExpenseNameDTO = await _get_expense_name(
            user_id=user_id, expense=expense, category=category, db=db
        )
        logger.info(f"Fetched expense_name: {expense_name}")
        new_expense: ExpenseResponse = await _create_expense(
            expense=expense, expense_name=expense_name, db=db
        )
        return new_expense

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def _get_expense_name(
    user_id: UUID, expense: ExpenseCreate, category: CategoryResponse, db: AsyncSession
) -> ExpenseNameDTO:
    """
    Get the expense name.

    Args:
        user_id (UUID): The user's unique identifier.
        expense (ExpenseCreate): The expense to create.
        category (CategoryResponse): The category of the expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseNameDTO: The expense name.
    """
    expense_name: Optional[ExpenseNameDTO] = await _find_expense_name(
        name=expense.name, db=db
    )
    return (
        expense_name
        if expense_name is not None
        else await _create_expense_name(
            user_id=user_id, name=expense.name, category_id=category.id, db=db
        )
    )


async def _create_expense(
    expense: ExpenseCreate, expense_name: ExpenseNameDTO, db: AsyncSession
) -> ExpenseResponse:
    """
    Create an expense.

    Args:
        expense (ExpenseCreate): The expense to create.
        expense_name (ExpenseNameDTO): The expense name to create.
        db (AsyncSession): The database session.

    Returns:
        ExpenseResponse: The created expense.
    """

    async def _create():
        new_expense = Expense(
            name_id=expense_name.id,
            user_id=expense_name.user_id,
            amount=expense.amount,
            date=expense.date,
        )
        logger.info(f"Creating expense: {new_expense.id}")
        db.add(new_expense)
        await db.commit()
        await db.refresh(new_expense)
        return ExpenseResponse(
            id=new_expense.id,
            name=expense_name.name,
            amount=new_expense.amount,
            date=new_expense.date,
            created_at=new_expense.created_at,
        )

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def _find_expense_name(name: str, db: AsyncSession) -> Optional[ExpenseNameDTO]:
    """
    Find an expense name by name.

    Args:
        name (str): The name of the expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseNameDTO | None: The expense name if found, otherwise None.
    """

    result = await db.execute(select(ExpenseName).filter(ExpenseName.name == name))
    expense_name: Optional[ExpenseName] = result.scalars().first()
    logger.info(f"Fetched expense_name: {expense_name}")
    return (
        ExpenseNameDTO(
            id=expense_name.id,
            category_id=expense_name.category_id,
            user_id=expense_name.user_id,
            name=expense_name.name,
        )
        if expense_name
        else None
    )


async def _create_expense_name(
    user_id: UUID, name: str, category_id: UUID, db: AsyncSession
) -> ExpenseNameDTO:
    """
    Create a new expense name.

    Args:
        user_id (UUID): The user's unique identifier.
        name (str): The name of the expense.
        category_id (UUID): The category's unique identifier.
        db (AsyncSession): The database session.

    Returns:
        ExpenseNameDTO: The created expense name.
    """

    async def _create():
        new_expense_name = ExpenseName(
            category_id=category_id, user_id=user_id, name=name
        )
        logger.info(f"Creating expense_name: {new_expense_name.name}")
        db.add(new_expense_name)
        await db.commit()
        await db.refresh(new_expense_name)
        return ExpenseNameDTO(
            id=new_expense_name.id,
            category_id=new_expense_name.category_id,
            user_id=new_expense_name.user_id,
            name=new_expense_name.name,
        )

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def _validate_data(
    user_id: UUID, category_name: str, db: AsyncSession
) -> CategoryResponse:
    """
    Validate user and category for creating an expense.

    Args:
        user_id (UUID): The user's unique identifier.
        category_name (str): The name of the category.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The category of the expense.
    """
    if not await v.user_exists(user_id=user_id, db=db):
        logger.error(f"User not found: {user_id}")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    category: Optional[CategoryResponse] = await category_service.get_by_name(
        name=category_name, db=db
    )
    return (
        category
        if category is not None
        else await category_service.create_category(name=category_name, db=db)
    )
