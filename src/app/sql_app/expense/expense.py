import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import User, ExpenseName


class Expense(Base):
    """
    Represents an Expense entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the expense.
        expense_name_id (uuid.UUID): Identifier for the associated expense name.
        user_id (uuid.UUID): Identifier for the associated user.
        created_at (datetime): Timestamp when the expense was created.
        updated_at (datetime): Timestamp when the expense was last updated.

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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(String, nullable=False, default=False)

    name: Mapped["ExpenseName"] = relationship("ExpenseName", back_populates="expenses")
    user: Mapped["User"] = relationship("User", back_populates="expenses")
