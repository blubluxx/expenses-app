import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import Expense, Category, User


class ExpenseName(Base):
    """
    Represents an Expense entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the expense.
        category_id (uuid.UUID): Identifier for the associated category.
        name (str): Name of the expense.

    Relationships:
        category (Category): The category associated with this expense name.
        expenses (list[Expense]): The expenses associated with this expense name.
    """

    __tablename__ = "expense_name"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "category_id",
            "user_id",
            name="unique_expense_name_per_user_and_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="expense_names", lazy="joined"
    )
    category: Mapped["Category"] = relationship(
        "Category", back_populates="expense_names", lazy="joined"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="name",
        uselist=True,
        collection_class=list,
        lazy="joined",
    )
