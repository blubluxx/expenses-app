from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

from app.schemas.common.enum import TimePeriod


class Token(BaseModel):
    """
    Pydantic class representing an access token.

    Attributes:
        header_payload (str): Payload of the token.
        signature (str): Signature of the JWT token.
    """

    header_payload: str
    signature: str


class FilterOptions(BaseModel):
    """
    Pydantic class representing filter options for expenses.

    Attributes:
        expense_name (str | None): The name of the expense.
        category (str | None): The category of the expense.
        start_date (str | None): The start date for filtering expenses.
        end_date (str | None): The end date for filtering expenses.
        min_amount (float | None): The minimum amount for filtering expenses.
        max_amount (float | None): The maximum amount for filtering expenses.
        time_period (str): The time period for grouping expenses.
        sort_by (str): The attribute to sort expenses by.
        order_by (str): The order to sort expenses by.

    """

    expense_name: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = datetime.now().strftime("%d-%m-%Y")
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    time_period: Optional[TimePeriod] = None
    sort_by: Literal["date", "amount"] = "date"
    order_by: Literal["asc", "desc"] = "desc"
    offset: int = 0
    limit: int = 10


class ResponseMessage(BaseModel):
    """
    Represents a response message for a request.
    """

    message: str
