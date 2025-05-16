import logging
from typing import Optional
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.common.application_error import ApplicationError
from app.schemas.user import UserResponse
from app.services.utils import processors as p
from app.sql_app.category.category import Category
from app.sql_app.custom_category.custom_category import CustomCategory
from app.sql_app.expense_category.expense_category import ExpenseCategory

logger = logging.getLogger(__name__)


async def create_custom_category(
    user_id: UUID, name: str, db: AsyncSession
) -> CategoryResponse:
    """
    Create a category.

    Args:
        user_id (UUID): The identifier of the user creating the category.
        name (str): The category name.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The created category.
    """

    existing_category: Optional[CategoryResponse] = await get_by_name(name=name, db=db)
    if existing_category:
        raise ApplicationError(
            detail=f"Category with name {name} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    async def _create_category():
        custom_category: CategoryResponse = await _create_custom_category(
            name=name, user_id=user_id, db=db
        )
        expense_category: CategoryResponse = await _create_expense_category(
            new_category=custom_category, db=db
        )

        return CategoryResponse(
            id=expense_category.id,
            name=expense_category.name,
        )

    return await p.process_db_transaction(
        transaction_func=_create_category,
        db=db,
    )


async def _create_custom_category(
    user_id: UUID, name: str, db: AsyncSession
) -> CategoryResponse:
    """
    Create a Custom Category.

    Args:
        user_id (UUID): The identifier of the user creating the category.
        name (str): The category name.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The created category.
    """

    async def _create():
        category = CustomCategory(name=name, user_id=user_id)
        logger.info(f"Creating custom category: {category.name}")
        _ = category.id
        db.add(category)
        await db.commit()
        await db.refresh(category)

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def _create_expense_category(
    new_category: CategoryResponse, db: AsyncSession
) -> CategoryResponse:
    """
    Create an Expense Category.

    Args:
        category_id (UUID): The identifier of the category.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The created category.
    """

    async def _create():
        category = ExpenseCategory(
            custom_category_id=new_category.id, name=new_category.name
        )
        logger.info(f"Creating category: {category.name}")
        db.add(category)
        await db.commit()
        await db.refresh(category)

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )

    return await p.process_db_transaction(
        transaction_func=_create,
        db=db,
    )


async def get_by_name(name: str, db: AsyncSession) -> Optional[CategoryResponse]:
    """
    Get a category by name.

    Args:
        name (str): The category name.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse | None: The category with the given name or None.
    """
    result = await db.execute(
        select(ExpenseCategory).filter(ExpenseCategory.name == name)
    )

    category = result.scalars().first()

    logger.info(f"Fetched category: {category.name if category else None}")

    return (
        CategoryResponse(
            id=category.id,
            name=category.name,
        )
        if category
        else None
    )


async def get_all(user: UserResponse, db: AsyncSession) -> list[CategoryResponse]:
    """
    Get all categories.

    Args:
        user (UserResponse): The user fetching the categories.
        db (AsyncSession): The database session.

    Returns:
        list[CategoryResponse]: A list of all categories.
    """

    result = await db.execute(
        select(Category.id, Category.name).union(
            select(CustomCategory.id, CustomCategory.name).filter(
                CustomCategory.user_id == user.id, CustomCategory.is_deleted == False
            )
        )
    )

    categories = result.all()
    logger.info(f"Fetched {len(categories)} categories")

    return [
        CategoryResponse(id=category_id, name=category_name)
        for category_id, category_name in categories
    ]
