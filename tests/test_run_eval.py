from unittest.mock import patch

from evaluation.run_eval import compare_systems
import subprocess
import sys


@patch("evaluation.run_eval.run_dataset")
def test_compare_systems_contains_baseline_and_agent(mock_run_dataset):
    mock_run_dataset.return_value = {"samples": [], "metrics": {}}
    result = compare_systems("evaluation/datasets/life_service_eval.json")
    assert "stacked_multi_agent" in result
    assert "baseline_single_agent" in result


def test_run_eval_script_executes():
    result = subprocess.run(
        [sys.executable, "evaluation/run_eval.py"],
        cwd="/Users/bytedance/Desktop/multi_agent_dialog_system",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


@patch("evaluation.run_eval.save_reports")
@patch("evaluation.run_eval.run_dataset")
def test_compare_systems_saves_reports(mock_run_dataset, mock_save_reports):
    mock_run_dataset.return_value = {"samples": [], "metrics": {}}
    mock_save_reports.return_value = {"json": "a.json", "html": "a.html", "svgs": {}}
    result = compare_systems("evaluation/datasets/life_service_eval.json")
    assert "reports" in result
