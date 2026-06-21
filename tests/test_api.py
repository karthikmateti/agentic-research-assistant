from fastapi.testclient import TestClient

from backend.agents.searcher import SearcherAgent
from backend.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        SearcherAgent,
        "search",
        lambda self, query, task_type: {
            "findings": ["Mock finding"],
            "references": [{"title": "Mock", "url": "https://example.com", "citation": "Mock citation"}],
            "source_links": ["https://example.com"],
        },
    )
    client = TestClient(app)
    response = client.post("/research", json={"query": "AI in healthcare", "report_mode": "short"})
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "topic_research"
    assert "Mock finding" in data["report"]


def test_history_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
