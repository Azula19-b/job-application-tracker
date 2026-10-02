"""Validation, search, filtering, and pipeline statistics tests."""

from tests.test_applications import API_PATH, application_payload


def test_invalid_status_returns_422(client):
    response = client.post(
        API_PATH,
        json=application_payload(application_status="Maybe Someday"),
    )
    assert response.status_code == 422


def test_invalid_salary_range_returns_422(client):
    response = client.post(
        API_PATH,
        json=application_payload(salary_min="150000", salary_max="100000"),
    )
    assert response.status_code == 422


def test_update_validates_merged_salary_range(client):
    application = client.post(API_PATH, json=application_payload()).json()
    response = client.patch(
        f"{API_PATH}/{application['id']}",
        json={"salary_min": "200000"},
    )
    assert response.status_code == 422


def test_filters_by_status_company_and_job_title(client):
    client.post(API_PATH, json=application_payload())
    client.post(
        API_PATH,
        json=application_payload(
            company_name="Northwind Analytics",
            job_title="Platform Engineer",
            application_status="Interview",
            interview_date="2026-10-20T10:00:00Z",
        ),
    )
    client.post(
        API_PATH,
        json=application_payload(
            company_name="Northwind Research",
            job_title="ML Engineer",
            application_status="Wishlist",
            application_date=None,
            follow_up_date=None,
        ),
    )

    assert len(client.get(API_PATH, params={"status": "Interview"}).json()) == 1
    assert len(client.get(API_PATH, params={"company": "northwind"}).json()) == 2
    assert len(client.get(API_PATH, params={"job_title": "platform"}).json()) == 1


def test_filters_follow_up_and_interview_dates(client):
    client.post(API_PATH, json=application_payload())
    client.post(
        API_PATH,
        json=application_payload(
            company_name="Later Follow Up",
            follow_up_date="2026-11-01",
            interview_date="2026-11-03T15:00:00Z",
        ),
    )

    follow_ups = client.get(API_PATH, params={"follow_up_before": "2026-10-10"})
    interviews = client.get(
        API_PATH,
        params={"interview_from": "2026-11-01T00:00:00Z"},
    )
    assert len(follow_ups.json()) == 1
    assert len(interviews.json()) == 1


def test_pipeline_statistics_include_all_statuses(client):
    client.post(API_PATH, json=application_payload())
    client.post(
        API_PATH,
        json=application_payload(company_name="Offer Co", application_status="Offer"),
    )
    response = client.get(f"{API_PATH}/stats")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["by_status"]["Applied"] == 1
    assert response.json()["by_status"]["Offer"] == 1
    assert response.json()["by_status"]["Rejected"] == 0
