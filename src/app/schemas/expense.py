from datetime import datetime
from typing import Optional
from uuid import UUID
from dateutil import parser

from pydantic import BaseModel, Field, field_validator
import pytz

from app.sql_app.expense.expense import Expense
from app.sql_app.expense_name.expense_name import ExpenseName


class ExpenseResponse(BaseModel):
    """
    A Pydantic model for an expense response.

    Attributes:
        id (UUID): The expense's unique identifier.
        name (str): The name of the expense.
        amount (float): The amount of the expense.
        category (str): The category of the expense.
        date (str): The date the expense was incurred.
        created_at (str): The timestamp when the expense was created.
        updated_at (str): The timestamp when the expense was last updated.
        note (str | None): The note associated with the expense.
    """

    id: UUID
    name: str
    amount: float
    category: str
    date: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator("date", mode="before")
    def date_to_str(cls, value) -> str:
        return value.strftime("%d-%m-%Y %H:%M")

    @field_validator("name", mode="before")
    def name_to_str(cls, value) -> str:
        return value.name if isinstance(value, ExpenseName) else value

    @classmethod
    def create(cls, expense: Expense) -> "ExpenseResponse":
        """
        Creates an ExpenseResponse object from an Expense object.

        Args:
            expense (Expense): The Expense object to create the ExpenseResponse from.

        Returns:
            ExpenseResponse: The created ExpenseResponse object.
        """
        user_timezone: str = expense.user.timezone
        user_tz = pytz.timezone(user_timezone)

        created_at: str = expense.created_at.astimezone(user_tz).strftime(
            "%d-%m-%Y %H:%M"
        )
        updated_at: str = expense.updated_at.astimezone(user_tz).strftime(
            "%d-%m-%Y %H:%M"
        )

        return ExpenseResponse(
            id=expense.id,
            name=expense.name,
            amount=expense.amount,
            category=expense.name.category.name,
            date=expense.date,
            created_at=created_at,
            updated_at=updated_at,
            note=expense.note,
        )


class ExpenseCreate(BaseModel):
    """
    A Pydantic model for creating an expense.

    Attributes:
        name (str): The name of the expense.
        amount (float): The amount of the expense.
        date (datetime): The date the expense was incurred.
        category (str): The category of the expense.
        note (str | None): The note associated with the expense.
    """

    name: str = Field(examples=["Expense name"])
    amount: float = Field(gt=0, examples=[100.0])
    date: datetime = Field(
        examples=["01/01/2025 12:00"], description="24h format is assumed"
    )
    category: str = Field(examples=["Category name"])
    note: Optional[str] = Field(examples=["Expense description"], default=None)

    class Config:
        from_attributes = True

    @field_validator("date", mode="before")
    def date_from_string(cls, date: str | datetime) -> datetime:
        """
        Converts a date <str> in the format d/m/y (passed as decimals) to a <datetime> object
        """

        return parser.parse(date) if isinstance(date, str) else date


class ExpenseUpdate(BaseModel):
    """
    A Pydantic model for updating an expense.

    Attributes:
        name (str | None): The name of the expense to be updated.
        amount (float | None): The amount of the expense to be updated.
        date (datetime | None): The date the expense to be updated was incurred.
        category (str | None): The category of the expense to be updated.
        note (str | None): The note associated with the expense to be updated
    """

    name: Optional[str] = Field(examples=["Expense name"], default=None)
    amount: Optional[float] = Field(gt=0, examples=[100.0], default=None)
    date: Optional[datetime] = Field(
        examples=["01/01/2022 12:00"], description="24h format is assumed", default=None
    )
    category: Optional[str] = Field(examples=["Category name"], default=None)
    note: Optional[str] = Field(examples=["Expense description"], default=None)

    class Config:
        from_attributes = True

    @field_validator("date", mode="before")
    def date_from_string(cls, date_str: str) -> datetime:
        """
        Converts a date <str> in the format d/m/y (passed as decimals) to a <datetime> object
        """

        return parser.parse(date_str)


class ExpenseNameDTO(BaseModel):
    """
    A Pydantic model for an expense name.

    Attributes:
        id (UUID): The expense name's unique identifier.
        category_id (UUID): The unique identifier of the associated category.
        user_id (UUID): The unique identifier of the user who created the expense name.
        name (str): The name of the expense.
    """

    id: UUID
    category_id: UUID
    user_id: UUID
    name: str

    class Config:
        from_attributes = True


class Note(BaseModel):
    """
    A Pydantic model for an expense note.

    Attributes:
        note (str): The note associated with the expense.
    """

    content: str = Field(examples=["Expense description"], min_length=1)
