"""REST API endpoints"""

from fastapi import APIRouter

from app.api.api_v1.routes import user_route
from app.api.api_v1.routes import auth_route

api_router = APIRouter()

api_router.include_router(user_route.router, prefix="/users", tags=["Users"])
api_router.include_router(auth_route.router, prefix="/auth", tags=["Authentication"])
