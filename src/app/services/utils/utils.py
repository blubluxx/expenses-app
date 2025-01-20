from typing import Optional

from passlib.hash import argon2
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


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

    coordinates: tuple = get_coordinates(city=city, country=country, state=state)
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
