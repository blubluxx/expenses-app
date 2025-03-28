import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import Expense, ExpenseName, CustomCategory


class User(Base):
    """
    Represents a User entity in the database.

    Attributes:
        id (uuid.UUID): Unique identifier of the user.
        username (str): Username of the user.
        email (str): Email of the user.
        password (str): Password of the user.
        timezone (str): Timezone of the user.
        created_at (datetime): Timestamp when the user was created. Default = Current time.
        is_admin (bool): Indicates if the user is an admin. Default = False.
        is_deleted (bool): Indicates if the user is deleted. Default = False.
        google_id (str): Google ID of the user, if applicable.

    Relationships:
        expenses (list[Expense]): The expenses associated with this user.
    """

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String, nullable=False, default="UTC")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    google_id: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="user", uselist=True, collection_class=list
    )
    expense_names: Mapped[list["ExpenseName"]] = relationship(
        "ExpenseName", back_populates="user", uselist=True, collection_class=list
    )
    custom_categories: Mapped[list["CustomCategory"]] = relationship(
        "CustomCategory", back_populates="user", uselist=True, collection_class=list
    )
