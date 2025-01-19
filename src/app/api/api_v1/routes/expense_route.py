from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserResponse
from app.sql_app.database import get_db
from app.schemas.expense import ExpenseCreate
from app.services import expense_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_user_expenses(
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get all expenses for a user.
    """

    async def _get_user_expenses():
        return await expense_service.get_user_expenses(user_id=user.id, db=db)

    return await process_request(
        get_entities_fn=_get_user_expenses,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="User not found.",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    expense: ExpenseCreate,
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _create_expense():
        return await expense_service.create_expense(
            user_id=user.id, expense=expense, db=db
        )

    return await process_request(
        get_entities_fn=_create_expense,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="User not found.",
    )


@router.patch(
    "/{expense_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth_service.get_current_user)],
)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _delete_expense():
        return await expense_service.delete_expense(expense_id=expense_id, db=db)

    return await process_request(
        get_entities_fn=_delete_expense,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Expense not found.",
    )
