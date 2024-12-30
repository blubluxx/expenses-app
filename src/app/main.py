from urllib.parse import urljoin
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import get_settings

from app.sql_app.database import initialize_database


def _setup_cors(app: FastAPI) -> None:
    """
    Set all CORS enabled origins
    """
    if get_settings().BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin) for origin in get_settings().BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=get_settings().PROJECT_NAME,
        openapi_url=urljoin(get_settings().API_V1_STR, "openapi.json"),
        version=get_settings().VERSION,
        docs_url="/docs",
        lifespan=lifespan,
    )
    app_.include_router(
        api_router,
        prefix=get_settings().API_V1_STR,
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
_setup_cors(app)
