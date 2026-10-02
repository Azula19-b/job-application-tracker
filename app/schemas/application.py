"""Validated API schemas for job application requests and responses."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

from app.models.application import ApplicationStatus


class JobApplicationBase(BaseModel):
    """Fields shared by create requests and database responses."""

    company_name: str = Field(min_length=1, max_length=200)
    job_title: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    job_url: HttpUrl | None = None
    salary_min: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    salary_max: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    application_status: ApplicationStatus = ApplicationStatus.WISHLIST
    application_date: date | None = None
    follow_up_date: date | None = None
    interview_date: datetime | None = None
    recruiter_name: str | None = Field(default=None, max_length=200)
    recruiter_email: EmailStr | None = None
    referral_contact: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=10_000)

    @model_validator(mode="after")
    def validate_ranges_and_dates(self) -> "JobApplicationBase":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError("salary_max must be greater than or equal to salary_min")
        if (
            self.application_date is not None
            and self.follow_up_date is not None
            and self.follow_up_date < self.application_date
        ):
            raise ValueError("follow_up_date cannot be before application_date")
        if (
            self.application_date is not None
            and self.interview_date is not None
            and self.interview_date.date() < self.application_date
        ):
            raise ValueError("interview_date cannot be before application_date")
        return self


class JobApplicationCreate(JobApplicationBase):
    """Payload for creating a tracked application."""


class JobApplicationUpdate(BaseModel):
    """Partial payload for changing an existing application."""

    company_name: str | None = Field(default=None, min_length=1, max_length=200)
    job_title: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    job_url: HttpUrl | None = None
    salary_min: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    salary_max: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    application_status: ApplicationStatus | None = None
    application_date: date | None = None
    follow_up_date: date | None = None
    interview_date: datetime | None = None
    recruiter_name: str | None = Field(default=None, max_length=200)
    recruiter_email: EmailStr | None = None
    referral_contact: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=10_000)

    @model_validator(mode="after")
    def validate_supplied_range(self) -> "JobApplicationUpdate":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return self


class JobApplicationRead(JobApplicationBase):
    """Complete application representation returned by the API."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationStats(BaseModel):
    """Counts used to summarize the current application pipeline."""

    total: int
    by_status: dict[str, int]
