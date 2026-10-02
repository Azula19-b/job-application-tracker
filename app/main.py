"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_db_and_tables
from app.routers import applications_router


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
