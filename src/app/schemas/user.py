from datetime import datetime
import re
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator, Field, EmailStr

from app.sql_app.user.user import User


PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,30}$"


class BaseUser(BaseModel):
    """
    A Pydantic model representing a base user.

    Attributes:
        username (str): The user's username.
        email (EmailStr): The user's email address.
    """

    username: str = Field(examples=["username_example"])
    email: EmailStr

    @field_validator("username")
    def validate_username(cls, value) -> str:
        if 5 > len(value) > 30:
            raise ValueError("Username must be between 5 and 30 characters long.")
        return value


class UserRegistration(BaseUser):
    """'
    A Pydantic model for user registration.

    Attributes:
        username (str): The user's username.
        password (str): The user's password.
        email (EmailStr): The user's email address.
        city (str): The user's city.
        state (str | None): The user's state.
        country (str): The user's country.

    Methods:
        validate_password: Validates the user's password.
        validate_username: Validates the user's username.
    """

    password: str = Field(examples=["Password_123!"])
    city: str = Field(examples=["Sofia"])
    state: Optional[str] = Field(examples=["State"], default=None)
    country: str = Field(examples=["Bulgaria"])

    @field_validator("password")
    def validate_password(cls, value) -> str:
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must be between 8 and 30 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
            )
        return value

    @field_validator("city")
    def validate_city(cls, value) -> str:
        if not all(char.isalpha() or char.isspace() for char in value):
            raise ValueError("City must contain only letters and spaces.")
        return value

    @field_validator("country")
    def validate_country(cls, value) -> str:
        if not all(char.isalpha() or char.isspace() for char in value):
            raise ValueError("City must contain only letters and spaces.")
        return value

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    A Pydantic model for user login.

    Attributes:
        username (str): The user's username.
        password (str): The user's password.

    """

    username: str = Field(examples=["username_example"])
    password: str = Field(examples=["Password_123!"])

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    A Pydantic model representing a User entity from the database.

    Attributes:
        id (UUID): The user's ID.
        username (str): The user's username.
        password (str): The user's password.
        email (str): The user's email.
        is_admin (bool): A boolean indicating if the user is an admin.
        is_deleted (bool): A boolean indicating if the user is deleted.
        created_at (str): The timestamp when the user was created.
        timezone (str): The user's timezone.
    """

    id: UUID
    username: str
    password: str
    email: EmailStr
    is_admin: bool
    is_deleted: bool
    created_at: str
    timezone: str

    class Config:
        from_attributes = True

    @classmethod
    def create(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            password=user.password,
            email=user.email,
            is_admin=user.is_admin,
            is_deleted=user.is_deleted,
            created_at=user.created_at,
            timezone=user.timezone,
        )

    @field_validator("created_at", mode="before")
    def created_at_to_str(cls, value: datetime) -> str:
        return value.strftime("%d-%m-%Y %H:%M %Z")


class UpdateUser(BaseModel):
    """
    A Pydantic model for updating user information.

    Attributes:
        username (str): The user's username.
        email (EmailStr): The user's email address.
        city (str): The user's city.
        state (str | None): The user's state.
        country (str): The user's country.
    """

    username: Optional[str] = Field(examples=["username_example"])
    email: Optional[EmailStr]
    timezone: Optional[str] = Field(examples=["UTC"])
    password: Optional[str] = Field(examples=["Password_123!"])
