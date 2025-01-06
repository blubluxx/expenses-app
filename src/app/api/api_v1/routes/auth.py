from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import UserLogin
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()

router.post("/login", description="Login a user", status_code=status.HTTP_200_OK)


def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _login():
        await auth_service.login(user, db)

    return process_request(
        get_entities_fn=_login,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not login user",
    )
