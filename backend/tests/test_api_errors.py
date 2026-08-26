"""API error handling — structured JSON error responses."""


def test_validation_error_returns_structured_json(client):
    response = client.post(
        "/matching/score",
        json={"job_title": "Dev"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["status"] == 422
    assert "fields" in body["error"]["details"]


def test_not_found_job_returns_structured_json(client):
    response = client.get("/jobs/99999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "http_error"
    assert body["error"]["status"] == 404


def test_unauthorized_without_token(client):
    response = client.get("/matching/students/me/recommendations")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["status"] == 401


def test_login_wrong_password(client, sample_student):
    response = client.post(
        "/auth/login",
        data={"username": sample_student.email, "password": "WrongPassword"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["status"] == 401
