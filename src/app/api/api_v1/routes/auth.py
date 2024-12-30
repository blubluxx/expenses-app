from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.sql_app.database import get_db
from app.schemas.user import User
from app.services import auth

router = APIRouter()


@router.post(
    "/register", description="Register a new user", status_code=status.HTTP_201_CREATED
)
def register(
    user: User,
    db: Session = Depends(get_db),
):
    pass
