import secrets
import requests
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth

from app.core.config import Settings, get_settings
from app.schemas.common.common import Token
from app.schemas.user import UserResponse
from app.services import auth_service, user_service
from app.services.utils import validators as v, utils as u

settings: Settings = get_settings()

FRONTEND_URL = str(settings.BACKEND_CORS_ORIGINS[0])
REDIRECT_URL: str = "http://127.0.0.1:8000/api/v1/google/callback"

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    redirect_uri=REDIRECT_URL,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)


async def login(request: Request):
    """
    Initiates the Google OAuth2 login process.

    This function generates a unique state token, stores it in the session,
    and redirects the user to the Google authorization URL.

    Args:
        request (Request): The HTTP request object.

    Returns:
        Response: A redirect response to the Google authorization URL.

    """
    request.session.clear()
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    return await oauth.google.authorize_redirect(
        request,
        REDIRECT_URL,
        state=state,
    )


async def callback(request: Request, db: AsyncSession) -> Response:
    """
    Handles the callback from Google after the user has authorized the application.
        This function verifies the state parameter, retrieves the access token,
        and fetches the user's information from Google.

        If the user is not registered, it registers them in the database.

        Finally, it generates an access token and sets it in the response cookies.

    Args:
        request (Request): The HTTP request object.
        db (AsyncSession): The database session.

    Returns:
        Response: A redirect response to the frontend URL with the access token set in cookies.

    Raises:
        HTTPException: If the state parameter is invalid or if there is an error during the OAuth process.
    """

    if request.query_params.get("state") != request.session.get("oauth_state"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    token = await oauth.google.authorize_access_token(request)

    user_info_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    google_response = requests.get(user_info_endpoint, headers=headers)

    user = google_response.json()
    logged_user: UserResponse = await _verify_user(user=user, db=db)

    data: dict = {"sub": str(logged_user.id)}
    access_token: Token = u.create_access_token(data=data)
    return auth_service.set_cookies(
        token=access_token, response=RedirectResponse(REDIRECT_URL)
    )


async def _verify_user(user: dict, db: AsyncSession) -> UserResponse:
    """
    Verify if the user is valid.

    Args:
        user (dict): The user data from Google.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The user response object.
    """
    user_email: str = user["email"]

    return (
        await user_service.get_by_email(email=user_email, db=db)
        if not await v.unique_email(email=user_email, db=db)
        else await register_new_google_user(user=user, user_email=user_email, db=db)
    )


async def register_new_google_user(
    user: dict, user_email: str, db: AsyncSession
) -> UserResponse:
    """
    Register a new Google user in the database.

    Args:
        user (dict): The user data from Google.
        user_email (str): The user's email address.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: The created user response object.

    """
    new_user: UserResponse = await user_service.create_new_user(
        username=user["name"],
        email=user_email,
        hashed_password=u.hash_password("default_password"),
        timezone="UTC",
        google_id=user["id"],
        db=db,
    )
    return new_user
