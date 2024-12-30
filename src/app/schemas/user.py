import re
from pydantic import BaseModel, field_validator, Field, EmailStr


PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,30}$"


class User(BaseModel):
    """'
    A Pydantic model for user registration.

    Attributes:
        username: str: The user's username.
        password: str: The user's password.
        email: EmailStr: The user's email address.

    Methods:
        validate_password: Validates the user's password.
        validate_username: Validates the user's username.
    """

    username: str = Field(examples=["username_example"])
    password: str = Field(examples=["Password_123!"])
    email: EmailStr

    @field_validator("password")
    def validate_password(cls, value) -> str:
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must be between 8 and 30 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
            )
        return value

    @field_validator("username")
    def validate_username(cls, value) -> str:
        if 5 > len(value) > 12:
            raise ValueError("Username must be between 5 and 12 characters long.")
        return value

    class Config:
        orm_mode = True
