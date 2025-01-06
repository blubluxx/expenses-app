from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import UserProfile
from app.services import user_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.post(
    "/signup", description="signup a new user", status_code=status.HTTP_201_CREATED
)
async def signup(
    user: UserProfile,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _signup():
        await user_service.signup(user, db)

    return process_request(
        get_entities_fn=_signup,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Could not register user",
    )
