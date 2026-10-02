"""REST endpoints for job application CRUD operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import JobApplication
from app.schemas.application import (
    JobApplicationCreate,
    JobApplicationRead,
    JobApplicationUpdate,
)
from app.services import applications as application_service


router = APIRouter(prefix="/applications", tags=["Applications"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ApplicationId = Annotated[int, Path(gt=0, description="Database ID of the application")]


def _application_or_404(db: Session, application_id: int) -> JobApplication:
    application = application_service.get_application(db, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job application {application_id} was not found.",
        )
    return application


@router.post("", response_model=JobApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: JobApplicationCreate,
    db: DatabaseSession,
) -> JobApplication:
    """Create a job application with validated tracking details."""

    return application_service.create_application(db, payload)


@router.get("", response_model=list[JobApplicationRead])
def list_applications(
    db: DatabaseSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[JobApplication]:
    """List applications with bounded offset pagination."""

    return application_service.list_applications(db, skip=skip, limit=limit)


@router.get("/{application_id}", response_model=JobApplicationRead)
def get_application(application_id: ApplicationId, db: DatabaseSession) -> JobApplication:
    """Retrieve one tracked application."""

    return _application_or_404(db, application_id)


@router.patch("/{application_id}", response_model=JobApplicationRead)
def update_application(
    application_id: ApplicationId,
    payload: JobApplicationUpdate,
    db: DatabaseSession,
) -> JobApplication:
    """Partially update an existing tracked application."""

    application = _application_or_404(db, application_id)
    return application_service.update_application(db, application, payload)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: ApplicationId, db: DatabaseSession) -> Response:
    """Permanently delete a tracked application."""

    application = _application_or_404(db, application_id)
    application_service.delete_application(db, application)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
