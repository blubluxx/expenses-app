import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.category import CategoryResponse
from app.schemas.common.messages import ResponseMessage
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseNameDTO,
    ExpenseUpdate,
    Note,
)
from app.services import category_service
from app.services.utils import validators as v, processors as p
from app.schemas.common.application_error import ApplicationError
from app.sql_app.expense.expense import Expense
from app.sql_app.expense_name.expense_name import ExpenseName

logger = logging.getLogger(__name__)


async def get_user_expenses(user_id: UUID, db: AsyncSession) -> list[ExpenseResponse]:
    """
    Get all expenses for a user with flag is_deleted == False.

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

    user_expenses = await db.execute(
        select(Expense).filter(Expense.user_id == user_id, Expense.is_deleted == False)
    )  # type: ignore
    expenses: list[Expense] = user_expenses.scalars().unique() or []  # type: ignore
    logger.info(f"Fetched all expenses for user: {user_id}")

    return [ExpenseResponse.create(expense=expense) for expense in expenses]


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
            user_id=user_id, expense_name=expense.name, category_id=category.id, db=db
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
    user_id: UUID, expense_name: str, category_id: UUID, db: AsyncSession
) -> ExpenseNameDTO:
    """
    Get the expense name.

    Args:
        user_id (UUID): The user's unique identifier.
        expense_name (str): The name of the expense.
        category_id (UUID): The category ID of the expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseNameDTO: The expense name.
    """
    existing_expense_name: Optional[ExpenseNameDTO] = await _find_expense_name(
        user_id=user_id, name=expense_name, db=db
    )
    return (
        existing_expense_name
        if existing_expense_name is not None
        else await _create_expense_name(
            user_id=user_id, name=expense_name, category_id=category_id, db=db
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
            date=expense.date,
            amount=expense.amount,
            note=expense.note,
        )
        logger.info(f"Creating expense: {new_expense.id}")
        db.add(new_expense)
        await db.commit()
        await db.refresh(new_expense)
        return ExpenseResponse.create(expense=new_expense)

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def _find_expense_name(
    user_id: UUID, name: str, db: AsyncSession
) -> Optional[ExpenseNameDTO]:
    """
    Find an expense name by name.

    Args:
        user_id (UUID): The user's unique identifier.
        name (str): The name of the expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseNameDTO | None: The expense name if found, otherwise None.
    """

    result = await db.execute(
        select(ExpenseName).filter(ExpenseName.name == name, Expense.user_id == user_id)
    )
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

    return await _get_category(category_name=category_name, db=db)


async def _get_category(category_name: str, db: AsyncSession) -> CategoryResponse:
    """
    Get the category of the expense.

    Args:
        category_name (str): The name of the category.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The category of the expense.
    """
    category: Optional[CategoryResponse] = await category_service.get_by_name(
        name=category_name, db=db
    )
    return (
        category
        if category is not None
        else await category_service.create_category(name=category_name, db=db)
    )


async def _get_by_id_db(expense_id: UUID, db: AsyncSession) -> Expense:
    """
    Get an expense by its unique identifier.

    Args:
        expense_id (UUID): The expense's unique identifier.
        db (AsyncSession): The database session.

    Returns:
        Expense: The expense if found.

    Raises:
        ApplicationError: If the expense is not found.
    """
    result = await db.execute(select(Expense).filter(Expense.id == expense_id))
    expense: Optional[Expense] = result.scalars().first()

    if expense is None:
        logger.error(f"Expense not found: {expense_id}")
        raise ApplicationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )
    logger.info(f"Fetched expense: {expense_id}")
    return expense


async def delete_expense(expense_id: UUID, db: AsyncSession) -> None:
    """
    Delete an expense.

    Args:
        expense_id (UUID): The expense's unique identifier.
        db (AsyncSession): The database session.
    """

    async def _delete():
        expense: Expense = await _get_by_id_db(expense_id=expense_id, db=db)
        expense.is_deleted = True
        await db.commit()
        logger.info(f"Deleted expense: {expense_id}")
        return ResponseMessage(message="Expense deleted.")

    return await p.process_db_transaction(
        transaction_func=_delete,
        db=db,
    )


async def update_expense(
    expense_id: UUID, expense_update: ExpenseUpdate, db: AsyncSession
) -> ExpenseResponse:
    """
    Update an expense.

    Args:
        expense_id (UUID): The expense's unique identifier.
        expense_update (ExpenseUpdate): The updated expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseResponse: The updated expense.
    """

    expense: Expense = await _get_by_id_db(expense_id=expense_id, db=db)
    updated_expense: ExpenseResponse = await _update_expense(
        expense=expense, expense_update=expense_update, db=db
    )
    logger.info(f"Updated expense: {expense_id}")
    return updated_expense


async def _update_expense(
    expense: Expense, expense_update: ExpenseUpdate, db: AsyncSession
) -> ExpenseResponse:
    """
    Update an expense.

    Args:
        expense (Expense): The expense to be updated.
        expense_update (ExpenseUpdate): The updated expense.
        db (AsyncSession): The database session.

    Returns:
        ExpenseResponse: The updated expense.
    """

    async def _update():
        if expense_update.name is not None:
            expense_name: ExpenseNameDTO = await _get_expense_name(
                user_id=expense.user_id,
                expense_name=expense_update.name,
                category_id=expense.name.category_id,
                db=db,
            )
            expense.name_id = expense_name.id
            logger.info(f"Updated expense_name: {expense_name}")
        if expense_update.amount is not None:
            expense.amount = expense_update.amount
            logger.info(f"Updated expense amount: {expense.amount}")
        if expense_update.date is not None:
            expense.date = expense_update.date
            logger.info(f"Updated expense date: {expense.date}")
        if expense_update.category is not None:
            category: CategoryResponse = await _get_category(
                category_name=expense_update.category, db=db
            )
            expense.name.category_id = category.id
            logger.info(f"Updated expense category: {category.name}")

        expense.note = expense_update.note
        logger.info(f"Updated expense note: {expense.note}")
        await db.commit()
        await db.refresh(expense)
        return ExpenseResponse.create(expense=expense)

    return await p.process_db_transaction(
        transaction_func=_update,
        db=db,
    )


async def add_note(expense_id: UUID, note: Note, db: AsyncSession) -> ExpenseResponse:
    """
    Add a note to an expense.

    Args:
        expense_id (UUID): The expense's unique identifier.
        note (Note): The note to add.
        db (AsyncSession): The database session.

    Returns:
        ExpenseResponse: The updated expense.
    """

    async def _add_note():
        expense: Expense = await _get_by_id_db(expense_id=expense_id, db=db)
        expense.note = note.content
        await db.commit()
        await db.refresh(expense)
        return ExpenseResponse.create(expense=expense)

    return await p.process_db_transaction(
        transaction_func=_add_note,
        db=db,
    )
