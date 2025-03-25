import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.expense_category.expense_category import ExpenseCategory


class Category(Base):
    """
    Represents an Category entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier for the category.
        name (str): Name of the category.

    Relationships:
        expense_names (list[ExpenseName]): The expense names associated with this category.
    """

    __tablename__ = "category"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    expense_categories: Mapped[list["ExpenseCategory"]] = relationship(
        "ExpenseCategory", back_populates="global_category"
    )
