import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryResponse
from app.services.utils import processors as p
from app.sql_app.category.category import Category

logger = logging.getLogger(__name__)


async def create_category(name: str, db: AsyncSession) -> CategoryResponse:
    """
    Create a category.

    Args:
        name (str): The category name.
        db (AsyncSession): The database session.

    Returns:
        CategoryResponse: The created category.
    """

    async def _create_category():
        category = Category(name=name)
        logger.info(f"Creating category: {category.name}")
        db.add(category)
        await db.commit()
        await db.refresh(category)

        return CategoryResponse(
            id=category.id,
            name=category.name,
        )

    return await p.process_db_transaction(
        transaction_func=_create_category,
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
    result = await db.execute(select(Category).filter(Category.name == name))
    category: Optional[Category] = result.scalars().first()
    logger.info(f"Fetched category: {category.name if category else None}")

    return (
        CategoryResponse(
            id=category.id,
            name=category.name,
        )
        if category
        else None
    )
