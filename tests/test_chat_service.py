from unittest.mock import patch

from app.services import chat_service
from app.state.session_store import chat_sessions


def teardown_function():
    chat_sessions.clear()


@patch("app.services.chat_service.load_knowledgebase")
def test_create_session_loads_knowledgebase_snapshot(mock_load_knowledgebase):
    mock_load_knowledgebase.return_value = {
        "restaurants": [{"name": "会话餐厅", "type": "火锅", "capacity": [2], "status": "有位"}],
        "hotels": [],
    }

    response = chat_service.create_session()
    session_state = chat_sessions[response["session_id"]]

    assert session_state["knowledgebase"]["restaurants"][0]["name"] == "会话餐厅"


@patch("app.services.chat_service.load_knowledgebase")
def test_reset_session_refreshes_knowledgebase_snapshot(mock_load_knowledgebase):
    mock_load_knowledgebase.side_effect = [
        {"restaurants": [{"name": "旧餐厅", "type": "火锅", "capacity": [2], "status": "有位"}], "hotels": []},
        {"restaurants": [{"name": "新餐厅", "type": "火锅", "capacity": [2], "status": "有位"}], "hotels": []},
    ]

    response = chat_service.create_session()
    session_id = response["session_id"]

    reset_response = chat_service.reset_session(session_id)
    session_state = chat_sessions[session_id]

    assert reset_response["session_id"] == session_id
    assert session_state["knowledgebase"]["restaurants"][0]["name"] == "新餐厅"
