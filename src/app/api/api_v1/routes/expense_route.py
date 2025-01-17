from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.services import expense_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def get_user_expenses(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get all expenses for a user.
    """

    async def _get_user_expenses():
        return await expense_service.get_user_expenses(user_id=user_id, db=db)

    return await process_request(
        get_entities_fn=_get_user_expenses,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="User not found.",
    )
