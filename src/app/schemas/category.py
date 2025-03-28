from uuid import UUID
from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    """
    A Pydantic model for a category response.

    Attributes:
        id (UUID): The category's unique identifier.
        name (str): The name of the category.
    """

    id: UUID
    name: str

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    """
    A Pydantic model for creating a category.

    Attributes:
        name (str): The name of the category.
    """

    name: str = Field(
        ...,
        title="Category name",
        description="The name of the category.",
        example="Groceries",
    )

    class Config:
        from_attributes = True
