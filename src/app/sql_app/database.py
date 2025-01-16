from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker


from app.core.config import get_settings, Settings


settings: Settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Dependency
async def get_db():
    """
    Provides a database session for use in a context manager.

    Yields:
        db: A database session object.

    Ensures that the database session is properly closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def create_uuid_extension():
    """
    Creates the "uuid-ossp" extension in the connected PostgreSQL database if it does not already exist.

    This function establishes a connection to the database using the provided engine,
    begins a transaction, and executes the SQL command to create the "uuid-ossp" extension.
    The "uuid-ossp" extension provides functions to generate universally unique identifiers (UUIDs).
    """
    async with engine.begin() as connection:
        await connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))


async def create_tables():
    """
    Create all tables in the database.

    This function uses SQLAlchemy's metadata to create all tables that are defined
    in the Base class. It binds the metadata to the specified engine and creates
    the tables if they do not already exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def is_database_initialized() -> bool:
    """
    Check if the database is already initialized by inspecting its tables.

    Returns:
        bool: True if tables exist, False otherwise.
    """
    async with engine.connect() as connection:
        result = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )
        return len(result) > 0


async def initialize_database():
    """
    Initialize the database by creating the tables and the "uuid-ossp" extension.

    This function calls the create_tables() and create_uuid_extension() functions
    to create the necessary tables and enable the "uuid-ossp" extension in the database.
    """
    if not await is_database_initialized():
        await create_uuid_extension()
        await create_tables()
