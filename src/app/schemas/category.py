from uuid import UUID
from pydantic import BaseModel


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
