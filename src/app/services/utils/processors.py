import logging
from typing import Callable, Any

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.schemas.common.application_error import ApplicationError

logger = logging.getLogger(__name__)


async def process_request(
    get_entities_fn: Callable,
    status_code: int,
    not_found_err_msg: str,
) -> JSONResponse:
    """
    Asynchronously processes a request by calling the provided function to get entities and returns an appropriate response.

    Args:
        get_entities_fn (Callable): A function that retrieves entities asynchronously.
        status_code (int): The HTTP status code to return in the response if successful.
        not_found_err_msg (str): The error message to log if a TypeError occurs.

    Returns:
        JSONResponse: A JSON response with the formatted data or a redirect response.

    Raises:
        ApplicationError: If an application-specific error occurs.
        TypeError: If a type error occurs, typically indicating a not found error.
        SyntaxError: If a syntax error occurs, typically indicating a bad request.
    """
    try:
        response = await get_entities_fn()

        formatted_response = _format_response(response)

        return JSONResponse(status_code=status_code, content=formatted_response)
    except ApplicationError as ex:
        logger.exception(str(ex))
        return JSONResponse(
            status_code=ex.data.status,
            content={"detail": {"error": ex.data.detail}},
        )
    except TypeError as ex:
        logger.exception(not_found_err_msg)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": {"error": str(ex)}},
        )
    except SyntaxError as ex:
        logger.exception("Pers thrown an exception")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"error": str(ex)}},
        )


async def process_db_transaction(transaction_func: Callable, db: AsyncSession) -> Any:
    """
    Executes a database transaction function and handles exceptions.

    Args:
        transaction_func (Callable): The function to execute within the transaction.
        db (Session): The SQLAlchemy database session.

    Returns:
        Any: The result of the transaction function if successful.

    Raises:
        ApplicationError: If an IntegrityError or SQLAlchemyError occurs during the transaction.
    """
    try:
        return await transaction_func()
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error: {str(e)}")
        raise ApplicationError(
            detail="Database conflict occurred", status_code=status.HTTP_409_CONFLICT
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Unexpected DB error: {str(e)}")
        raise ApplicationError(
            detail=f"{str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _format_response(data) -> dict:
    """
    Formats the response data to include the detail key.

    Args:
        data (Union[BaseModel, list[BaseModel]]): The data to format.

    Returns:
        dict: The formatted response data.
    """
    if isinstance(data, list):
        return {"detail": [item.model_dump(mode="json") for item in data]}
    return {
        "detail": data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    }
