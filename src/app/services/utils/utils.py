import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import HTTPException, status
from passlib.hash import argon2
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import Settings, get_settings
from app.schemas.common.common import Token

settings: Settings = get_settings()
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hashes the given password using bcrypt.
    """
    return argon2.hash(password)


def verify_password(password, hashed_password) -> bool:
    """
    Vefifies user password against hashed password stored in the database

    Args:
        password: str: The user's password.
        hashed_password: str: The hashed password stored in the database.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return not argon2.verify(password, hashed_password)


def get_timezone(city: str, country: str, state: str | None = None) -> Optional[str]:
    """
    Get the timezone of a location.

    Args:
        city (str): The city name.
        state (str | None): The state or region name (optional).
        country (str): The country name.

    Returns:
        str | None: The timezone of the location, if found.
    """

    coordinates: Optional[tuple[float, float]] = get_coordinates(
        city=city, country=country, state=state
    )
    if not coordinates:
        return None
    tf = TimezoneFinder()

    return tf.timezone_at(lat=coordinates[0], lng=coordinates[1])


def get_coordinates(
    city: str, country: str, state: str | None = None
) -> Optional[tuple[float, float]]:
    """
    Get the latitude and longitude of a location.

    Args:
        city (str): The city name.
        state (str): The state or region name (optional).
        country (str): The country name (optional).

    Returns:
        tuple | None: Latitude and longitude as floats, or None if not found.
    """
    geolocator = Nominatim(user_agent="expenses-app", timeout=2)  # Increase timeout
    location_query = f"{city}, {state}, {country}" if state else f"{city}, {country}"

    location = geolocator.geocode(location_query)

    return (location.latitude, location.longitude) if location else None


def create_access_token(data: dict) -> Token:
    """
    Creates an access token.

    Args:
        data (dict): The data to encode.

    Returns:
        Token: The access token.

    Raises:
        HTTPException: If the token cannot be created.

    """
    token = create_jwt_token(data=data)
    header_payload = ".".join(token.split(".")[:2])
    signature = str(token.split(".")[2])
    return Token(header_payload=header_payload, signature=signature)


def create_jwt_token(data: dict) -> str:
    """
    Creates a JWT token.

    Args:
        data (dict): The data to encode.

    Returns:
        str: The access token.

    Raises:
        HTTPException: If the token cannot be created.

    """
    try:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        token: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        logger.info(msg="Created access token")

        return token

    except JWTError:
        raise HTTPException(
            detail="Could not create token",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Verifies the provided JWT access token.

    Args:
        token (str): The JWT access token to be verified.

    Returns:
        dict[str, Any]: The decoded payload of the token if verification is successful.

    Raises:
        HTTPException: If the token has expired or cannot be verified.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        logger.info("Decoded token payload")
        return payload
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        logger.error("Could not verify token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify token",
        )
