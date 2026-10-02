"""CRUD API tests for job applications."""


API_PATH = "/api/v1/applications"


def application_payload(**overrides):
    payload = {
        "company_name": "Cloud Systems Inc.",
        "job_title": "Cloud Engineer",
        "location": "Remote",
        "job_url": "https://example.com/jobs/123",
        "salary_min": "110000.00",
        "salary_max": "145000.00",
        "application_status": "Applied",
        "application_date": "2026-10-01",
        "follow_up_date": "2026-10-08",
        "recruiter_name": "Taylor Morgan",
        "recruiter_email": "taylor@example.com",
        "notes": "Submitted through the company careers page.",
    }
    payload.update(overrides)
    return payload


def test_create_application(client):
    response = client.post(API_PATH, json=application_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["company_name"] == "Cloud Systems Inc."
    assert body["application_status"] == "Applied"
    assert body["created_at"]


def test_retrieve_all_and_single_application(client):
    first = client.post(API_PATH, json=application_payload()).json()
    client.post(
        API_PATH,
        json=application_payload(company_name="DataWorks", job_title="Data Engineer"),
    )

    collection = client.get(API_PATH)
    single = client.get(f"{API_PATH}/{first['id']}")

    assert collection.status_code == 200
    assert len(collection.json()) == 2
    assert single.status_code == 200
    assert single.json()["job_title"] == "Cloud Engineer"


def test_update_application(client):
    application = client.post(API_PATH, json=application_payload()).json()
    response = client.patch(
        f"{API_PATH}/{application['id']}",
        json={
            "application_status": "Interview",
            "interview_date": "2026-10-15T14:30:00Z",
            "notes": "First interview scheduled.",
        },
    )
    assert response.status_code == 200
    assert response.json()["application_status"] == "Interview"
    assert response.json()["interview_date"].startswith("2026-10-15T14:30:00")


def test_delete_application(client):
    application = client.post(API_PATH, json=application_payload()).json()
    response = client.delete(f"{API_PATH}/{application['id']}")
    assert response.status_code == 204
    assert client.get(f"{API_PATH}/{application['id']}").status_code == 404


def test_invalid_application_id_returns_404(client):
    response = client.get(f"{API_PATH}/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job application 99999 was not found."
