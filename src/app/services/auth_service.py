import logging
from datetime import datetime, timedelta
from typing import Any, Union
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings, Settings
from app.sql_app.database import get_db
from app.schemas.user import UserLogin, UserResponse
from app.schemas.common.common import Token
from app.services.utils import utils as u, validators as v, processors as p
from app.services import user_service
from app.schemas.common.application_error import ApplicationError

settings: Settings = get_settings()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


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
    access_token: Token = _create_access_token(data=data)

    return _set_cookies(token=access_token)


async def logout(request: Request) -> Response:
    """
    Logs out the user by deleting the access and refresh tokens from cookies.

    Args:
        request (Request): The request object.

    Returns:
        Response: The HTTP response object with cookies deleted.
    """
    try:
        response = JSONResponse({"msg": "Logged out."})
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="none",
        )

        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to log you out",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _set_cookies(token: Token) -> Response:
    """
    Sets a secure HTTP-only cookie with the provided token.

    Args:
        token (Token): The token object containing the access token.

    Returns:
        Response: A JSON response indicating successful login with the cookie set.

    Raises:
        HTTPException: If there is an error setting the cookie, an HTTP 500 error is raised with the exception details.
    """
    try:
        response = JSONResponse({"msg": "Logged in."})
        response.set_cookie(
            key="token",
            value=token.access_token,
            httponly=True,
            secure=True,
            samesite="none",
        )
        logger.info(msg="Set cookie")
        return response
    except KeyError as e:
        raise HTTPException(
            detail=f"Exception occurred: {e}, unable to set cookies",
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
    user_db: UserResponse = await user_service.get_by_username(
        username=user.username, db=db
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


def _create_access_token(data: dict) -> Token:
    """
    Creates an access token.

    Args:
        data (dict): The data to encode.

    Returns:
        Token: The access token.

    Raises:
        HTTPException: If the token cannot be created.

    """
    try:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        token: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        logger.info(msg="Created access token")
        return Token(access_token=token, token_type="bearer")
    except JWTError:
        raise HTTPException(
            detail="Could not create token",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _verify_access_token(token: str) -> dict[str, Any]:
    """
    Verifies the provided JWT access token.

    Args:
        token (str): The JWT access token to be verified.

    Returns:
        dict[str, Any]: The decoded payload of the token if verification is successful.

    Raises:
        HTTPException: If the token has expired or cannot be verified.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        logger.info("Decoded token payload")
        return payload
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        logger.error("Could not verify token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify token",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
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
    payload: dict = _verify_access_token(token)
    user_id: Union[Any, None] = payload.get("sub")

    user: UserResponse = await user_service.get_by_id(user_id=UUID(user_id), db=db)

    return user
