import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import User


class CustomCategory(Base):
    """
    Represents a Custom category defined by a User.

    Attributes:
        id (uuid.UUID): Unique identifier for the custom category.
        name (str): Name of the custom category.
        user_id (uuid.UUID): ID of the user assiciated with this category.
    """

    __tablename__ = "custom_category"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="custom_categories", lazy="joined"
    )
