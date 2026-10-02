"""SQLAlchemy engine, session factory, and FastAPI database dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def _engine_options(database_url: str) -> dict:
    """Return safe engine options for PostgreSQL and test-friendly SQLite."""

    options: dict = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    return options


engine = create_engine(settings.database_url, **_engine_options(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_db_and_tables() -> None:
    """Create tables for simple deployments that do not yet use migrations."""

    # Import models before create_all so their table metadata is registered.
    from app.models.application import JobApplication  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session per API request."""

    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
