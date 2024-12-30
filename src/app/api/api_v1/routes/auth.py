from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import User
from app.services import auth
from app.services.utils.processors import process_request

router = APIRouter()


@router.post(
    "/register", description="Register a new user", status_code=status.HTTP_201_CREATED
)
async def register(
    user: User,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _register():
        await auth.register(user, db)

    return process_request(
        get_entities_fn=_register,
        status_code=status.HTTP_201_CREATED,
        not_found_err_msg="Could not register user",
    )
