import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common.application_error import ApplicationError
from app.sql_app.database import get_db
from app.schemas.user import UserLogin, UserResponse
from app.schemas.common.common import Token
from app.services.utils import utils as u, validators as v, processors as p
from app.services import user_service


logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def login(login_data: OAuth2PasswordRequestForm, db: AsyncSession) -> Response:
    """
    Login a user.

    Args:
        login_data (OAuth2PasswordRequestForm): UserLogin data.
        db (AsyncSession): The database session.

    Returns:
        Response: A JSON response indicating successful login with the cookie set.
    """
    user: UserLogin = UserLogin(
        username=login_data.username, password=login_data.password
    )

    user_id: UUID = await _authenticate_user(user=user, db=db)
    data: dict = {"sub": str(user_id)}
    access_token: Token = u.create_access_token(data=data)
    response = JSONResponse({"msg": "Logged in."})

    return set_cookies(token=access_token, response=response)


async def logout(request: Request) -> Response:
    """
    Logs out the user by deleting the access and refresh tokens from cookies.

    Args:
        request (Request): The request object.

    Returns:
        Response: The HTTP response object with cookies deleted.
    """
    try:
        request.cookies.clear()
        response = JSONResponse({"msg": "Logged out."})
        response.delete_cookie(
            key="uId",
            httponly=False,
            secure=True,
            samesite="none",
        )
        response.delete_cookie(
            key="ATS",
            httponly=True,
            secure=True,
            samesite="none",
        )
        logger.info(msg="Deleted cookie")
        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to log you out",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def _authenticate_user(user: UserLogin, db: AsyncSession) -> UUID:
    """
    Authenticates a user.

    Args:
        user (UserLogin): The user to authenticate.
        db (AsyncSession): The database session.

    Returns:
        UUID: The ID of the user.

    Raises:
        HTTPException: If the password is wrong.
    """
    try:
        user_db: UserResponse = await user_service.get_by_username(
            username=user.username, db=db
        )
    except ApplicationError:
        logger.error(msg="Passwords do not match")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such user exists"
        )

    stored_password: str = user_db.password
    if not u.verify_password(
        password=user_db.password, hashed_password=stored_password
    ):
        logger.error(msg="Passwords do not match")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    return user_db.id


def set_cookies(token: Token, response: Response) -> Response:
    """
    Sets cookies with header+payload and signature.

    Args:
        token(Token): Dictionary containing header_payload and signature.

    Returns:
        Response: A JSON response indicating successful login with cookies set.
    """
    try:
        response.set_cookie(
            key="uId",
            value=token.header_payload,
            httponly=False,
            secure=True,
            samesite="none",
        )

        response.set_cookie(
            key="ATS",
            value=token.signature,
            httponly=True,
            secure=True,
            samesite="none",
        )
        logger.info(msg="Set cookies")
        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to set cookies",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Retrieve the current user based on the provided access token.

    Args:
        token (str): The access token provided by the user.
        db (AsyncSession): The database session dependency.

    Returns:
        UserResponse: The user information corresponding to the provided token.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    token_payload: Optional[str] = request.cookies.get("uId")
    token_signature: Optional[str] = request.cookies.get("ATS")

    if not token_payload or not token_signature:
        logger.error("Token payload or signature is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
        )

    token: str = f"{token_payload}.{token_signature}"
    payload: dict = u.verify_access_token(token)
    user_id: Optional[Any] = payload.get("sub")

    user: UserResponse = await user_service.get_by_id(user_id=UUID(user_id), db=db)

    return user


async def require_admin_role(
    user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if not user.is_admin:
        logger.error(msg="User does not have admin role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. User does not have admin role.",
        )

    return user
