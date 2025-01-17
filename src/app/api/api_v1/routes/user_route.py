from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import UserRegistration
from app.services import user_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.post(
    "/signup", description="Register a new user", status_code=status.HTTP_201_CREATED
)
async def signup(
    user: UserRegistration,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _signup():
        return await user_service.signup(user, db)

    return await process_request(
        get_entities_fn=_signup,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Could not register user",
    )
