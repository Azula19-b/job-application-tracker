"""Persistence operations for job applications."""

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.application import JobApplication
from app.schemas.application import JobApplicationCreate, JobApplicationUpdate


APPLICATION_FIELDS = (
    "company_name",
    "job_title",
    "location",
    "job_url",
    "salary_min",
    "salary_max",
    "application_status",
    "application_date",
    "follow_up_date",
    "interview_date",
    "recruiter_name",
    "recruiter_email",
    "referral_contact",
    "notes",
)


def _storage_values(payload: JobApplicationCreate) -> dict:
    """Convert validated Pydantic values into database-friendly Python values."""

    values = payload.model_dump()
    if values.get("job_url") is not None:
        values["job_url"] = str(values["job_url"])
    return values


def create_application(db: Session, payload: JobApplicationCreate) -> JobApplication:
    """Create and return a job application in one transaction."""

    application = JobApplication(**_storage_values(payload))
    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except SQLAlchemyError:
        db.rollback()
        raise
    return application


def get_application(db: Session, application_id: int) -> JobApplication | None:
    """Return one application by primary key."""

    return db.get(JobApplication, application_id)


def list_applications(db: Session, skip: int = 0, limit: int = 100) -> list[JobApplication]:
    """Return applications ordered by most recently updated."""

    statement: Select = (
        select(JobApplication)
        .order_by(JobApplication.updated_at.desc(), JobApplication.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def update_application(
    db: Session,
    application: JobApplication,
    payload: JobApplicationUpdate,
) -> JobApplication:
    """Validate merged state, then update an application transactionally."""

    current_values = {field: getattr(application, field) for field in APPLICATION_FIELDS}
    current_values.update(payload.model_dump(exclude_unset=True))
    validated = JobApplicationCreate.model_validate(current_values)

    for field, value in _storage_values(validated).items():
        setattr(application, field, value)

    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except SQLAlchemyError:
        db.rollback()
        raise
    return application


def delete_application(db: Session, application: JobApplication) -> None:
    """Delete an application in one transaction."""

    try:
        db.delete(application)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
