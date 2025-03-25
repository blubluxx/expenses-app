import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import Category, CustomCategory, ExpenseName


class ExpenseCategory(Base):
    """
    Links an expense name to either a global category or a custom category.

    Args:
        Optional[uuid.UUID]: The identifier of the global category.
        Optional[uuid.UUID]: The identifier of the custom category.
        name (str): The name of the category.

    Constraints:
        - Either `global_category_id` or `custom_category_id` must be set, but not both.
    """

    __tablename__ = "expense_category"
    __table_args__ = (
        CheckConstraint(
            "(global_category_id IS NOT NULL AND custom_category_id IS NULL) OR "
            "(global_category_id IS NULL AND custom_category_id IS NOT NULL)",
            name="check_only_one_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    global_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=True
    )
    custom_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("custom_category.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(nullable=False)

    global_category: Mapped["Category"] = relationship(
        "Category", back_populates="expense_categories"
    )
    custom_category: Mapped["CustomCategory"] = relationship(
        "CustomCategory", back_populates="expense_categories"
    )
    expense_names: Mapped[list["ExpenseName"]] = relationship(
        "ExpenseName", back_populates="category"
    )
