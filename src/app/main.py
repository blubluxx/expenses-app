from urllib.parse import urljoin
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v1.api import api_router
from app.core.config import get_settings, Settings

from app.sql_app.database import initialize_database

settings: Settings = get_settings()


def _setup_cors(app: FastAPI) -> None:
    """
    Set all CORS enabled origins
    """
    if settings.BACKEND_CORS_ORIGINS:
        origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=urljoin(settings.API_V1_STR, "openapi.json"),
        version=settings.VERSION,
        docs_url="/docs",
        lifespan=lifespan,
    )
    app_.include_router(
        api_router,
        prefix=settings.API_V1_STR,
    )
    return app_


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle the lifespan of the FastAPI application.
    """
    await initialize_database()
    yield


app = _create_app()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
_setup_cors(app)
