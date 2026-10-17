from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class FakeTinyFish:
    def start(self, query: str) -> dict[str, str]:
        return {"research_run_id": "test-run-123", "error": None}

    def get_run(self, research_run_id: str) -> dict:
        return {
            "research_run_id": research_run_id,
            "query": "Can AI detect river pollution using satellite imagery?",
            "status": "COMPLETED",
            "deep_result": {
                "result": "A report with a real citation.",
                "citations": ["https://example.org/paper"],
            },
            "evidence": [],
            "research_plan": [],
            "iterations": 1,
            "error": None,
        }


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_run_uses_tinyfish_provider(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_tinyfish_client", lambda: FakeTinyFish())
    response = client.post(
        "/api/research-runs",
        json={"question": "Can AI detect river pollution using satellite imagery?"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["run_id"] == "test-run-123"
    assert body["status"] == "QUEUED"
    assert len(body["stages"]) == 5


def test_get_run_normalizes_report_and_citations(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_tinyfish_client", lambda: FakeTinyFish())
    response = client.get("/api/research-runs/test-run-123")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["report"] == "A report with a real citation."
    assert body["citations"] == [{"url": "https://example.org/paper", "title": ""}]


def test_create_run_rejects_blank_question() -> None:
    response = client.post("/api/research-runs", json={"question": "   "})
    assert response.status_code == 422


def test_create_run_rejects_too_long_question() -> None:
    response = client.post("/api/research-runs", json={"question": "x" * 1001})
    assert response.status_code == 422
