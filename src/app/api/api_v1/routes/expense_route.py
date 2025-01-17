from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.sql_app.database import get_db
from app.schemas.user import UserRegistration
from app.services import user_service
from app.services import auth_service
from app.services.utils.processors import process_request

router = APIRouter()
