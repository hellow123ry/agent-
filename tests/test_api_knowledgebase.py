from fastapi.testclient import TestClient

from app.server import app
from app.services import knowledgebase_service


client = TestClient(app)


def test_get_knowledgebase_returns_envelope(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)

    response = client.get("/api/knowledgebase")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert "restaurants" in body["data"]
    assert "hotels" in body["data"]


def test_update_restaurants_returns_envelope(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)

    response = client.put(
        "/api/knowledgebase/restaurants",
        json={
            "restaurants": [
                {
                    "name": "新餐厅",
                    "type": "烧烤",
                    "capacity": [2, 6],
                    "status": "有位",
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["restaurants"][0]["name"] == "新餐厅"


def test_update_hotels_validation_error_uses_envelope(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)

    response = client.put(
        "/api/knowledgebase/hotels",
        json={
            "hotels": [
                {
                    "name": "坏酒店",
                    "location": "市中心",
                    "type": "商务",
                    "price": -88,
                    "status": "有房",
                }
            ]
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["field"] == "hotels[0].price"
