from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


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
        orm_mode = True

    @property
    def date(self) -> datetime:
        return self.date.strftime("%d-%m-%Y %H:%M")

    @property
    def created_at(self) -> datetime:
        return self.date.strftime("%d-%m-%Y %H:%M")
