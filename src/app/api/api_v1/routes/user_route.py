from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import BaseUser, UpdateUser, UserRegistration, UserResponse
from app.services import user_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()


@router.post(
    "/verify",
    description="Verify if user data is unique in the database",
    status_code=status.HTTP_200_OK,
)
async def verify(
    user_data: BaseUser, db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    async def _verify():
        return await user_service.verify_user(user_data, db)

    return await process_request(
        get_entities_fn=_verify,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not verify user data",
    )


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


@router.get(
    "/all",
    description="Get all users",
    dependencies=[Depends(auth_service.require_admin_role)],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    offset: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    async def _get_all():
        return await user_service.get_all(db=db, offset=offset, limit=limit)

    return await process_request(
        get_entities_fn=_get_all,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not fetch users",
    )


@router.patch(
    "/{user_id}/role",
    description="Update user role",
    dependencies=[Depends(auth_service.require_admin_role)],
    status_code=status.HTTP_200_OK,
)
async def change_user_role(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    async def _change_user_role():
        return await user_service.change_user_role(user_id=id, db=db)

    return await process_request(
        get_entities_fn=_change_user_role,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not change user role",
    )


@router.put(
    "/",
    description="Update user data",
    status_code=status.HTTP_200_OK,
)
async def update_user(
    update_data: UpdateUser,
    user: UserResponse = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async def _update():
        return await user_service.update_user(user=user, update_data=update_data, db=db)

    return await process_request(
        get_entities_fn=_update,
        status_code=status.HTTP_200_OK,
        not_found_err_msg="Could not update user",
    )
