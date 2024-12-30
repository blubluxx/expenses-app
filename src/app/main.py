from urllib.parse import urljoin

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import get_settings


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
    )
    app_.include_router(
        api_router,
        prefix=get_settings().API_V1_STR,
    )
    return app_


app = _create_app()
_setup_cors(app)
