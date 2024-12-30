from pydantic import BaseModel


class ResponseMessage(BaseModel):
    """
    Represents a response message for a request.
    """

    message: str
