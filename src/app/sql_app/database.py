from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

engine = create_engine(get_settings().DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency
def get_db():
    """
    Provides a database session for use in a context manager.

    Yields:
        db: A database session object.

    Ensures that the database session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_uuid_extension():
    """
    Creates the "uuid-ossp" extension in the connected PostgreSQL database if it does not already exist.

    This function establishes a connection to the database using the provided engine,
    begins a transaction, and executes the SQL command to create the "uuid-ossp" extension.
    The "uuid-ossp" extension provides functions to generate universally unique identifiers (UUIDs).
    """
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))


def create_tables():
    """
    Create all tables in the database.

    This function uses SQLAlchemy's metadata to create all tables that are defined
    in the Base class. It binds the metadata to the specified engine and creates
    the tables if they do not already exist.
    """
    Base.metadata.create_all(bind=engine)


def is_database_initialized():
    """
    Check if the database is already initialized by inspecting its tables.

    Returns:
        bool: True if tables exist, False otherwise.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return len(tables) > 0


def initialize_database():
    """
    Initialize the database by creating the tables and the "uuid-ossp" extension.

    This function calls the create_tables() and create_uuid_extension() functions
    to create the necessary tables and enable the "uuid-ossp" extension in the database.
    """
    if not is_database_initialized():
        create_uuid_extension()
        create_tables()
