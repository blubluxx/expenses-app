from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserResponse
from app.schemas.common.enum import TimePeriod
from app.sql_app.database import get_db
from app.services import data_analysis_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.get(
    "/{time_period}",
    status_code=status.HTTP_200_OK,
    description="Get the total expenses for a user in a given time period.",
)
async def analyze_expenses(
    time_period: TimePeriod,
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get the total expenses for a user in a given time period.
    """

    async def _analyze_expenses():
        return await data_analysis_service.analyze_expenses_time_period(
            user_id=user.id, time_period=time_period, db=db
        )

    return await process_request(
        get_entities_fn=_analyze_expenses,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="User not found.",
    )
