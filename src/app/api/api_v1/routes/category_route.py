from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import CategoryCreate
from app.schemas.user import UserResponse
from app.sql_app.database import get_db
from app.services import category_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Create a new category.",
)
async def create_category(
    category_name: CategoryCreate,
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _create_category():
        return await category_service.create_custom_category(
            user_id=user.id, name=category_name.name, db=db
        )

    return await process_request(
        get_entities_fn=_create_category,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Could not create category",
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    description="Get all categories.",
)
async def get_categories(
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get all categories.
    """

    async def _get_categories():
        return await category_service.get_all(user=user, db=db)

    return await process_request(
        get_entities_fn=_get_categories,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Cannot fetch categories.",
    )
