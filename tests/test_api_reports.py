from fastapi.testclient import TestClient

from app.server import app


client = TestClient(app)


def test_reports_latest_returns_existing_artifacts():
    response = client.get("/api/reports/latest")
    assert response.status_code == 200
    body = response.json()
    assert "latest_html" in body
    assert "latest_json" in body


def test_reports_history_returns_list():
    response = client.get("/api/reports/history")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["items"], list)


def test_reports_file_serves_latest_html():
    response = client.get("/api/reports/file", params={"path": "latest.html"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
