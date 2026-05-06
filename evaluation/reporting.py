from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _metric_rows(result: dict) -> list[tuple[str, float, float]]:
    metrics = [
        ("task_success_rate", "任务成功率"),
        ("average_turns", "平均轮次"),
        ("slot_f1", "槽位 F1"),
    ]
    rows = []
    for key, label in metrics:
        rows.append(
            (
                label,
                result["stacked_multi_agent"]["metrics"].get(key, 0.0),
                result["baseline_single_agent"]["metrics"].get(key, 0.0),
            )
        )
    return rows


def save_evaluation_result(result: dict, output_dir: str | Path) -> dict:
    output_path = _ensure_output_dir(output_dir)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_path / f"{run_id}.json"
    latest_path = output_path / "latest.json"
    json_text = json.dumps(result, ensure_ascii=False, indent=2)
    json_path.write_text(json_text, encoding="utf-8")
    latest_path.write_text(json_text, encoding="utf-8")
    return {"json": str(json_path), "latest_json": str(latest_path), "run_id": run_id}


def generate_html_report(result: dict, output_dir: str | Path, report_name: str) -> str:
    output_path = _ensure_output_dir(output_dir)
    html_path = output_path / f"{report_name}.html"
    rows = "".join(
        f"<tr><td>{label}</td><td>{stacked:.4f}</td><td>{baseline:.4f}</td></tr>"
        for label, stacked, baseline in _metric_rows(result)
    )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>评测报告</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .charts img {{ max-width: 320px; margin-right: 16px; }}
  </style>
</head>
<body>
  <h1>评测报告</h1>
  <table>
    <thead>
      <tr><th>指标</th><th>多 Agent</th><th>Baseline</th></tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")
    return str(html_path)


def _build_svg(metric_name: str, stacked_value: float, baseline_value: float) -> str:
    width = 420
    height = 240
    max_value = max(stacked_value, baseline_value, 1.0)
    stacked_height = int((stacked_value / max_value) * 140)
    baseline_height = int((baseline_value / max_value) * 140)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="20" y="30" font-size="18">{metric_name}</text>
  <line x1="60" y1="180" x2="360" y2="180" stroke="black"/>
  <rect x="110" y="{180 - stacked_height}" width="60" height="{stacked_height}" fill="#4f81bd"/>
  <rect x="240" y="{180 - baseline_height}" width="60" height="{baseline_height}" fill="#c0504d"/>
  <text x="100" y="205" font-size="14">Multi-Agent</text>
  <text x="240" y="205" font-size="14">Baseline</text>
  <text x="115" y="{170 - stacked_height}" font-size="12">{stacked_value:.2f}</text>
  <text x="245" y="{170 - baseline_height}" font-size="12">{baseline_value:.2f}</text>
</svg>"""


def generate_metric_svgs(result: dict, output_dir: str | Path, report_name: str) -> dict:
    output_path = _ensure_output_dir(output_dir)
    metrics = {
        "task_success_rate": "任务成功率",
        "average_turns": "平均轮次",
        "slot_f1": "槽位 F1",
    }
    output = {}
    for metric_key, metric_label in metrics.items():
        svg_path = output_path / f"{report_name}-{metric_key}.svg"
        svg_text = _build_svg(
            metric_label,
            result["stacked_multi_agent"]["metrics"].get(metric_key, 0.0),
            result["baseline_single_agent"]["metrics"].get(metric_key, 0.0),
        )
        svg_path.write_text(svg_text, encoding="utf-8")
        output[metric_key] = str(svg_path)
    return output


def save_reports(result: dict, output_dir: str | Path = "evaluation/results") -> dict:
    persisted = save_evaluation_result(result, output_dir)
    report_name = persisted["run_id"]
    html_path = generate_html_report(result, output_dir, report_name)
    latest_html = generate_html_report(result, output_dir, "latest")
    svg_paths = generate_metric_svgs(result, output_dir, report_name)
    latest_svgs = generate_metric_svgs(result, output_dir, "latest")
    return {
        "json": persisted["json"],
        "latest_json": persisted["latest_json"],
        "html": html_path,
        "latest_html": latest_html,
        "svgs": svg_paths,
        "latest_svgs": latest_svgs,
    }
