from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes the given password using bcrypt.
    """
    hash_password = context.hash(password)

    return hash_password


def verify_password(password, hashed_password) -> bool:
    """
    Vefifies user password against hashed password stored in the database

    Args:
        password: str: The user's password.
        hashed_password: str: The hashed password stored in the database.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return context.verify(password, hashed_password)
