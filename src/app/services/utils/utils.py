from passlib.hash import argon2


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
    return argon2.verify(password, hashed_password)
