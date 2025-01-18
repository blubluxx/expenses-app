from datetime import datetime
from uuid import UUID
from dateutil import parser

from pydantic import BaseModel, Field, field_validator

from app.sql_app.expense_name.expense_name import ExpenseName


class ExpenseResponse(BaseModel):
    """
    A Pydantic model for an expense response.

    Attributes:
        id (UUID): The expense's unique identifier.
        name (str): The name of the expense.
        date (datetime): The date the expense was incurred.
        created_at (datetime): The timestamp when the expense was created.
        amount (float): The amount of the expense.
    """

    id: UUID
    name: str
    amount: float
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("date")
    def date(cls, value) -> str:
        return value.strftime("%d-%m-%Y %H:%M")

    @field_validator("created_at")
    def created_at(cls, value) -> str:
        return value.strftime("%d-%m-%Y %H:%M")

    @field_validator("name", mode="before")
    def name(cls, value) -> str:
        return value.name if isinstance(value, ExpenseName) else value


class ExpenseCreate(BaseModel):
    """
    A Pydantic model for creating an expense.

    Attributes:
        name (str): The name of the expense.
        amount (float): The amount of the expense.
        date (datetime): The date the expense was incurred.
        category (str): The category of the expense.
    """

    name: str = Field(examples=["Expense name"])
    amount: float = Field(gt=0, examples=[100.0])
    date: str = Field(
        examples=["01/01/2022 12:00"], description="24h format is assumed"
    )
    category: str = Field(examples=["Category name"])

    class Config:
        from_attributes = True

    @field_validator("date")
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
