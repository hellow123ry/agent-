from pathlib import Path

from evaluation.reporting import (
    generate_html_report,
    generate_metric_svgs,
    save_evaluation_result,
)


def sample_result():
    return {
        "stacked_multi_agent": {
            "metrics": {
                "task_success_rate": 1.0,
                "average_turns": 2.75,
                "slot_f1": 0.75,
            },
            "samples": [],
        },
        "baseline_single_agent": {
            "metrics": {
                "task_success_rate": 0.75,
                "average_turns": 2.75,
                "slot_f1": 0.0,
            },
            "samples": [],
        },
    }


def test_save_evaluation_result(tmp_path):
    output = save_evaluation_result(sample_result(), tmp_path)
    assert Path(output["json"]).exists()


def test_generate_html_report(tmp_path):
    html_path = generate_html_report(sample_result(), tmp_path, "latest")
    assert Path(html_path).exists()
    assert Path(html_path).read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_generate_metric_svgs(tmp_path):
    svg_paths = generate_metric_svgs(sample_result(), tmp_path, "latest")
    assert len(svg_paths) == 3
    assert all(Path(path).exists() for path in svg_paths.values())
