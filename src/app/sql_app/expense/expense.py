import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import User, ExpenseName


class Expense(Base):
    """
    Represents an Expense entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the expense.
        name_id (uuid.UUID): Identifier for the associated expense name.
        user_id (uuid.UUID): Identifier for the associated user.
        date (datetime): Date when the expense was incurred.
        amount (float): Amount of the expense.
        created_at (datetime): Timestamp when the expense was created.
        updated_at (datetime): Timestamp when the expense was last updated.
        is_deleted (bool): Flag indicating if the expense has been

    Relationships:
        expense_name (ExpenseName): The name of the expense.
    """

    __tablename__ = "expense"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    name_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("expense_name.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    note: Mapped[str] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    name: Mapped["ExpenseName"] = relationship(
        "ExpenseName", back_populates="expenses", lazy="joined"
    )
    user: Mapped["User"] = relationship("User", back_populates="expenses")
