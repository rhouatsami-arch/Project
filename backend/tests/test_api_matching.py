"""API integration tests — matching score and recommendations."""


def test_compute_match_score(client):
    response = client.post(
        "/matching/score",
        json={
            "technical_skills": "python,fastapi,sql",
            "cv_extracted_text": "3 ans d'expérience Python FastAPI PostgreSQL",
            "field_of_study": "Computer Science",
            "location": "Paris",
            "job_title": "Backend Developer",
            "job_description": "Python FastAPI developer with 2 years experience",
            "required_skills": "python,fastapi|optional:docker",
            "job_location": "Paris",
            "employment_type": "full_time",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["compatibility_score"] <= 100
    assert "rank_label" in data
    assert "breakdown" in data
    assert "skills_score" in data["breakdown"]
    assert "python" in data["breakdown"]["matched_skills"]


def test_calculate_matching_score_endpoint(client):
    response = client.post(
        "/matching/calculate",
        json={
            "technical_skills": "python,sql",
            "job_title": "Data Analyst",
            "job_description": "SQL and Python data analysis",
            "required_skills": "python,sql",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["final_score"] <= 1.0
    assert "explanation_data" in data
    assert "matched_skills" in data["explanation_data"]


def test_student_recommendations(client, auth_headers_student, sample_job):
    response = client.get(
        "/matching/students/me/recommendations?limit=5&min_score=0",
        headers=auth_headers_student,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    top = data[0]
    assert top["job"]["title"] == sample_job.title
    assert 0 <= top["compatibility_score"] <= 100
    assert "breakdown" in top
    assert "explanation" in top


def test_recommendations_require_auth(client):
    response = client.get("/matching/students/me/recommendations")
    assert response.status_code == 401
