"""API smoke tests — health and pipeline metadata."""


def test_health_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "MatiousHire API"
    assert "version" in data


def test_matching_pipeline_info(client):
    response = client.get("/matching/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "2.1.0"
    assert "weights" in data
    assert data["weights"]["skills"] == 0.35
    assert len(data["stages"]) >= 5
