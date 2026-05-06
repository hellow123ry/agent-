from unittest.mock import patch

from evaluation.systems import build_state, run_system_turns


def test_build_state_contains_required_fields():
    state = build_state()
    assert "messages" in state
    assert "task_stack" in state
    assert "global_blackboard" in state


@patch("evaluation.systems.load_knowledgebase")
def test_build_state_loads_knowledgebase_snapshot(mock_load_knowledgebase):
    mock_load_knowledgebase.return_value = {
        "restaurants": [{"name": "测试餐厅", "type": "火锅", "capacity": [2], "status": "有位"}],
        "hotels": [{"name": "测试酒店", "location": "望京", "type": "经济", "price": 399, "status": "有房"}],
    }

    state = build_state()

    assert state["knowledgebase"]["restaurants"][0]["name"] == "测试餐厅"
    assert state["knowledgebase"]["hotels"][0]["name"] == "测试酒店"


@patch("evaluation.systems.run_dialog")
def test_run_system_turns_returns_final_state(mock_run_dialog):
    state = build_state()
    mock_run_dialog.return_value = state
    result = run_system_turns("stacked_multi_agent", state, ["你好"])
    assert "messages" in result
    assert "task_stack" in result
