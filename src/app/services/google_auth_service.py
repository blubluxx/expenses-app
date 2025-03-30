from typing import Optional

import secrets
import httpx

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.schemas.common.common import Token
from app.schemas.user import UserResponse
from app.services import auth_service, user_service
from app.services.utils import utils as u

settings: Settings = get_settings()

FRONTEND_URL = str(settings.BACKEND_CORS_ORIGINS[0])
REDIRECT_URL = settings.GOOGLE_REDIRECT_URL
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


async def login(request: Request) -> Response:
    """
    Initiates the Google OAuth2 login process.

    This function generates a unique state token, stores it in the session,
    and redirects the user to the Google authorization URL.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: A redirect response to the Google authorization URL.

    """
    state = secrets.token_urlsafe(16)
    token = u.create_jwt_token(data={"state": state})

    url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URL}&scope=openid%20profile%20email&state={token}"

    return RedirectResponse(url=url)


async def callback(request: Request, db: AsyncSession) -> Response:
    """
    Handles the callback from Google after the user has authorized the application.
        This function verifies the state parameter, retrieves the access token,
        and fetches the user's information from Google.

        If the user is not registered, it registers them in the database.

        Finally, it generates an access token and sets it in the response cookies.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: A redirect response to the frontend URL with the access token set in cookies.
    """
    code = request.query_params.get("code")
    jwt_token = request.query_params.get("state")

    u.verify_access_token(token=jwt_token)

    google_token = await _get_google_token(code=code)

    google_user = await _get_google_user_info(token=google_token, db=db)

    data: dict = {"sub": str(google_user.id)}
    access_token: Token = u.create_access_token(data=data)
    response = RedirectResponse(
        url=FRONTEND_URL,
    )
    return auth_service.set_cookies(token=access_token, response=response)


async def _get_google_token(code: str) -> str:
    """
    Retrieves the access token from Google using the authorization code.

    Args:
        code (str): The authorization code received from Google.

    Returns:
        str: The response containing the access token and other information.

    Raises:
        HTTPException: If the token retrieval fails.
    """
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URL,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_response_data = token_response.json()

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token",
        )

    return token_response_data.get("access_token")


async def _get_google_user_info(token: str, db: AsyncSession) -> dict:
    """
    Retrieves user information from Google using the access token.

    Args:
        token (str): The access token.
        db (AsyncSession): The database session.

    Returns:
        dict: The user information.

    Raises:
        HTTPException: If the user information retrieval fails.
    """
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token}"}
        )
        user_info_response.raise_for_status()
        user = user_info_response.json()

    return await _verify_user(user=user, db=db)


async def _verify_user(user: dict, db: AsyncSession) -> UserResponse:
    """
    Verify if the user is valid.

    Args:
        user (dict): The user data from Google.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The user response object.
    """

    existing_user: Optional[UserResponse] = await user_service.get_by_google_id(
        google_id=user["id"], db=db
    )

    return (
        existing_user
        if existing_user
        else await register_new_google_user(user=user, db=db)
    )


async def register_new_google_user(user: dict, db: AsyncSession) -> UserResponse:
    """
    Register a new Google user in the database.

    Args:
        user (dict): The user data from Google.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The created user response object.

    """
    new_user: UserResponse = await user_service.create_new_user(
        username=user["email"],
        email=user["email"],
        hashed_password=u.hash_password("default_password"),
        timezone="UTC",
        google_id=user["id"],
        db=db,
    )
    return new_user
