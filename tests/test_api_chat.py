from fastapi.testclient import TestClient
from unittest.mock import patch

from app.server import app


client = TestClient(app)


def test_create_chat_session():
    response = client.post("/api/chat/session")
    assert response.status_code == 200
    body = response.json()
    assert "session_id" in body
    assert body["messages"] == []
    assert body["state"]["active_task"] == ""


@patch("app.services.chat_service.run_dialog")
def test_send_chat_turn_returns_messages_and_state(mock_run_dialog):
    session_id = client.post("/api/chat/session").json()["session_id"]
    mock_run_dialog.return_value = {
        "messages": [
            {"type": "human", "content": "你好"},
            {"type": "ai", "content": "你好，有什么可以帮你？"},
        ],
        "current_intent": "unknown",
        "active_task": "",
        "task_stack": [],
        "global_blackboard": {},
    }
    response = client.post(
        f"/api/chat/session/{session_id}/turn",
        json={"message": "你好"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert len(body["messages"]) >= 2
    assert body["messages"][0]["role"] == "user"
    assert "state" in body
    assert "traces" in body


def test_get_and_delete_chat_session():
    session_id = client.post("/api/chat/session").json()["session_id"]

    get_response = client.get(f"/api/chat/session/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json()["session_id"] == session_id

    delete_response = client.delete(f"/api/chat/session/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["messages"] == []
