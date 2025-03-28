from fastapi import Request, Response
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
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=REDIRECT_URL,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid profile email"},
)


async def login(request: Request):
    request.session.clear()

    return await oauth.google.authorize_redirect(
        request, REDIRECT_URL, prompt="consent"
    )


async def callback(request: Request, db: AsyncSession) -> Response:
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]
    logged_user: UserResponse = await _verify_user(user=user, db=db)

    data: dict = {"sub": str(logged_user.id)}
    access_token: Token = u.create_access_token(data=data)
    response = RedirectResponse(FRONTEND_URL)
    response = auth_service.set_cookies(token=access_token, response=response)
    return response


async def _verify_user(user: dict, db: AsyncSession) -> UserResponse:
    """
    Verify if the user is valid.

    Args:
        user (dict): The user data from Google.

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
    """
    google_id = user["sub"]
    new_user: UserResponse = await user_service.create_new_user(
        username=user_email,
        email=user_email,
        hashed_password=u.hash_password("default_password"),
        timezone="UTC",
        google_id=google_id,
        db=db,
    )
    return new_user
