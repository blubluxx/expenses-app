from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import google_auth
from app.sql_app.database import get_db

router = APIRouter()


@router.get(
    "/login",
    status_code=status.HTTP_200_OK,
    description="Google Auth",
)
async def login(
    request: Request,
):
    return await google_auth.login(request=request)


@router.get(
    "/callback",
    status_code=status.HTTP_200_OK,
    description="Google Auth Callback",
)
async def callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return await google_auth.callback(request=request, db=db)
