from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.services import auth_service

router = APIRouter()


@router.post("/login", description="Login a user", status_code=status.HTTP_200_OK)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Response:
    return await auth_service.login(login_data=login_data, db=db)


@router.post(
    "/logout",
    description="Logs out the current user by invalidating their existing tokens.",
)
async def logout(
    request: Request, token: str = Depends(auth_service.oauth2_scheme)
) -> Response:
    response = await auth_service.logout(request=request)
    response.status_code = status.HTTP_200_OK
    return response
