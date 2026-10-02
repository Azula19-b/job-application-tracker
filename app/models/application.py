"""Database model for a tracked job application."""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApplicationStatus(StrEnum):
    """Supported stages in the job application lifecycle."""

    WISHLIST = "Wishlist"
    APPLIED = "Applied"
    REFERRAL_REQUESTED = "Referral Requested"
    RECRUITER_SCREEN = "Recruiter Screen"
    INTERVIEW = "Interview"
    TECHNICAL_INTERVIEW = "Technical Interview"
    FINAL_INTERVIEW = "Final Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class JobApplication(Base):
    """A company role and its progress through the application lifecycle."""

    __tablename__ = "job_applications"
    __table_args__ = (
        CheckConstraint("salary_min IS NULL OR salary_min >= 0", name="salary_min_positive"),
        CheckConstraint("salary_max IS NULL OR salary_max >= 0", name="salary_max_positive"),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_max >= salary_min",
            name="salary_range_valid",
        ),
        Index("ix_job_applications_company_name", "company_name"),
        Index("ix_job_applications_job_title", "job_title"),
        Index("ix_job_applications_status", "application_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    job_url: Mapped[str | None] = mapped_column(String(2048))
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    application_status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=False),
        nullable=False,
        default=ApplicationStatus.WISHLIST,
    )
    application_date: Mapped[date | None] = mapped_column(Date)
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recruiter_name: Mapped[str | None] = mapped_column(String(200))
    recruiter_email: Mapped[str | None] = mapped_column(String(320))
    referral_contact: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
