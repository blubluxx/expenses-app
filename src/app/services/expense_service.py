import logging
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.schemas.user import UserRegistration, UserResponse
from app.schemas.common.messages import ResponseMessage
from app.services.utils import processors as p, validators as v, utils as u
from app.schemas.common.application_error import ApplicationError
from app.sql_app.user.user import User

logger = logging.getLogger(__name__)
