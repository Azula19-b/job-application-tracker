"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import create_db_and_tables
from app.routers import applications_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize database tables when enabled for simple deployments."""

    if settings.create_tables_on_startup:
        create_db_and_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A cloud-ready REST API for tracking job applications, interviews, "
        "follow-ups, contacts, and outcomes."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.include_router(applications_router, prefix=settings.api_v1_prefix)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_: Request, error: SQLAlchemyError) -> JSONResponse:
    """Return a safe response while preserving database details in server logs."""

    logger.exception("Database operation failed", exc_info=error)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "The database is temporarily unavailable."},
    )


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Describe the service and point clients to interactive documentation."""

    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Expose a lightweight container and load-balancer health check."""

    return {"status": "healthy", "environment": settings.environment}
