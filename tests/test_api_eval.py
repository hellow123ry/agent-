from fastapi.testclient import TestClient
from unittest.mock import patch

from app.server import app


client = TestClient(app)


def test_start_eval_job():
    response = client.post(
        "/api/eval/run",
        json={"dataset_path": "evaluation/datasets/life_service_eval.json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"
    assert "job_id" in body


def test_get_eval_job_status():
    body = client.post(
        "/api/eval/run",
        json={"dataset_path": "evaluation/datasets/life_service_eval.json"},
    ).json()
    response = client.get(f"/api/eval/jobs/{body['job_id']}")
    assert response.status_code == 200
    assert response.json()["job_id"] == body["job_id"]
    assert "progress" in response.json()


def test_get_missing_eval_result_returns_404():
    response = client.get("/api/eval/jobs/not-exist/result")
    assert response.status_code == 404


@patch("app.api.eval.start_eval_job")
def test_start_eval_job_uses_service(mock_start_eval_job):
    mock_start_eval_job.return_value = {
        "job_id": "eval_test",
        "status": "running",
        "progress": {
            "stacked_multi_agent": {"completed_samples": 0, "total_samples": 22},
            "baseline_single_agent": {"completed_samples": 0, "total_samples": 22},
        },
    }
    response = client.post(
        "/api/eval/run",
        json={"dataset_path": "evaluation/datasets/life_service_eval.json"},
    )
    assert response.status_code == 200
    assert response.json()["job_id"] == "eval_test"
