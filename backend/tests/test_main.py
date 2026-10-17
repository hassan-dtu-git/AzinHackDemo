from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_run_accepts_question_without_faking_research() -> None:
    response = client.post(
        "/api/research-runs",
        json={"question": "Can AI detect river pollution using satellite imagery?"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending_integration"
    assert len(body["stages"]) == 5
    assert "No sources or findings have been generated" in body["message"]


def test_create_run_rejects_blank_question() -> None:
    response = client.post("/api/research-runs", json={"question": "   "})
    assert response.status_code == 422


def test_create_run_rejects_too_long_question() -> None:
    response = client.post("/api/research-runs", json={"question": "x" * 1001})
    assert response.status_code == 422
