from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()

router.post("/login", description="Login a user", status_code=status.HTTP_200_OK)


def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _login():
        await auth_service.login(login_data=login_data, db=db)

    return process_request(
        get_entities_fn=_login,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not login user",
    )


@router.post(
    "/logout",
    description="Logs out the current user by invalidating their existing tokens.",
)
def logout(request: Request) -> Response:
    response = auth_service.logout(request=request)
    response.status_code = status.HTTP_200_OK
    return response
