from unittest.mock import patch
import time

from evaluation.runner import (
    check_success,
    extract_predicted_slots,
    run_dataset,
    run_sample,
)


@patch("evaluation.runner.run_sample")
def test_run_dataset_returns_summary(mock_run_sample):
    mock_run_sample.return_value = {
        "id": "sample-1",
        "success": True,
        "turn_count": 2,
        "predicted_slots": {"location": "北京"},
        "expected_slots": {"location": "北京"},
        "final_reply": "好的",
    }
    result = run_dataset(
        "evaluation/datasets/life_service_eval.json", "stacked_multi_agent"
    )
    assert "samples" in result
    assert "metrics" in result


def test_extract_predicted_slots_normalizes_basic_values():
    state = {
        "global_blackboard": {
            "location": "  北京  ",
            "people_count": "3",
            "date": "明天入住",
        }
    }
    assert extract_predicted_slots(state) == {
        "location": "北京",
        "people_count": 3,
        "date": "明天",
    }


def test_check_success_requires_all_rule_groups():
    sample = {
        "expected_slots": {"location": "北京", "people_count": 3},
        "success_conditions": {
            "contains_all": ["北京", "烤肉"],
            "not_contains_any": ["抱歉"],
            "required_slots": ["location", "people_count"],
        },
    }

    success, reasons = check_success(
        sample,
        final_reply="已为您查询到北京烤肉店，3位可安排。",
        predicted_slots={"location": "北京", "people_count": 3},
        final_state={"active_task": "dining", "task_stack": []},
    )

    assert success is True
    assert reasons == []


def test_check_success_returns_failure_reasons():
    sample = {
        "expected_slots": {"location": "北京"},
        "success_conditions": {
            "contains_all": ["北京", "烤肉"],
            "not_contains_any": ["抱歉"],
            "required_slots": ["location"],
            "active_task_is": "dining",
        },
    }

    success, reasons = check_success(
        sample,
        final_reply="抱歉，暂时没有结果。",
        predicted_slots={},
        final_state={"active_task": "hotel", "task_stack": []},
    )

    assert success is False
    assert any("contains_all" in reason for reason in reasons)
    assert any("not_contains_any" in reason for reason in reasons)
    assert any("required_slots" in reason for reason in reasons)
    assert any("active_task_is" in reason for reason in reasons)


@patch("evaluation.runner.run_system_turns")
@patch("evaluation.runner.build_state")
def test_run_sample_includes_failure_reasons(mock_build_state, mock_run_system_turns):
    mock_build_state.return_value = {"messages": [], "global_blackboard": {}}
    mock_run_system_turns.return_value = {
        "messages": [type("Message", (), {"content": "抱歉，暂时没有结果。"})()],
        "global_blackboard": {},
        "active_task": "hotel",
        "task_stack": [],
    }
    sample = {
        "id": "sample-1",
        "user_turns": ["帮我查北京烤肉"],
        "expected_slots": {"location": "北京"},
        "success_conditions": {
            "contains_all": ["北京", "烤肉"],
            "required_slots": ["location"],
            "active_task_is": "dining",
        },
    }

    result = run_sample(sample, "stacked_multi_agent")

    assert result["success"] is False
    assert "failure_reasons" in result
    assert result["failure_reasons"]


@patch("evaluation.runner.run_system_turns")
@patch("evaluation.runner.build_state")
def test_run_sample_times_out(mock_build_state, mock_run_system_turns):
    mock_build_state.return_value = {"messages": [], "global_blackboard": {}}

    def slow_run(*args, **kwargs):
        time.sleep(0.05)
        return {"messages": [], "global_blackboard": {}, "active_task": "", "task_stack": []}

    mock_run_system_turns.side_effect = slow_run
    sample = {
        "id": "slow-sample",
        "user_turns": ["帮我查酒店"],
        "expected_slots": {},
        "success_conditions": {"contains_any": ["酒店"]},
    }

    result = run_sample(sample, "stacked_multi_agent", sample_timeout_seconds=0.01)

    assert result["success"] is False
    assert "timeout" in result["final_reply"].lower()
    assert any("sample_timeout" in reason for reason in result["failure_reasons"])
