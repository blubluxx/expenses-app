"""REST API endpoints"""

from fastapi import APIRouter

from app.api.api_v1.routes import user_route
from app.api.api_v1.routes import auth_route
from app.api.api_v1.routes import expense_route
from app.api.api_v1.routes import category_route
from app.api.api_v1.routes import analysis_route

api_router = APIRouter()

api_router.include_router(user_route.router, prefix="/users", tags=["Users"])
api_router.include_router(auth_route.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(expense_route.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(
    category_route.router, prefix="/categories", tags=["Categories"]
)
api_router.include_router(analysis_route.router, prefix="/analysis", tags=["Analysis"])
