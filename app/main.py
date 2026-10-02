"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings


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
