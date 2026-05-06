import json
from pathlib import Path


def test_eval_dataset_schema():
    data = json.loads(
        Path("evaluation/datasets/life_service_eval.json").read_text(encoding="utf-8")
    )
    assert isinstance(data, list)
    sample = data[0]
    assert "id" in sample
    assert "domain" in sample
    assert "user_turns" in sample
    assert "expected_slots" in sample
    assert "success_conditions" in sample
    assert len(data) >= 20
    allowed_condition_keys = {
        "contains_any",
        "contains_all",
        "not_contains_any",
        "required_slots",
        "forbidden_slots",
        "active_task_is",
        "task_stack_depth_at_least",
    }
    for item in data:
        assert isinstance(item["user_turns"], list)
        assert isinstance(item["expected_slots"], dict)
        assert isinstance(item["success_conditions"], dict)
        assert set(item["success_conditions"]).issubset(allowed_condition_keys)
