from __future__ import annotations

import multiprocessing
from multiprocessing import Process, Queue
from queue import Empty
from threading import Thread
from uuid import uuid4

from app.state.session_store import eval_jobs
from evaluation.reporting import save_reports
from evaluation.runner import run_dataset


def _run_eval_worker(job_id: str, dataset_path: str, queue: Queue) -> None:
    result: dict = {}
    systems = ["stacked_multi_agent", "baseline_single_agent"]
    try:
        for system_name in systems:
            queue.put(
                {
                    "type": "system_started",
                    "job_id": job_id,
                    "system": system_name,
                }
            )
            system_result = run_dataset(
                dataset_path,
                system_name,
                progress_callback=lambda sample_result, completed, total, callback_system_name: queue.put(
                    {
                        "type": "sample_progress",
                        "job_id": job_id,
                        "system": callback_system_name,
                        "completed_samples": completed,
                        "total_samples": total,
                    }
                ),
            )
            result[system_name] = system_result
            queue.put(
                {
                    "type": "system_completed",
                    "job_id": job_id,
                    "system": system_name,
                    "metrics": system_result["metrics"],
                }
            )

        result["reports"] = save_reports(result)
        queue.put({"type": "completed", "job_id": job_id, "result": result})
    except Exception as exc:  # pragma: no cover - defensive
        queue.put({"type": "failed", "job_id": job_id, "error": str(exc)})


def _consume_eval_queue(job_id: str, queue: Queue, process: Process) -> None:
    while process.is_alive() or not queue.empty():
        try:
            event = queue.get(timeout=0.2)
        except Empty:
            continue

        job = eval_jobs.get(job_id)
        if not job:
            continue

        event_type = event["type"]
        if event_type == "system_started":
            job["current_system"] = event["system"]
        elif event_type == "sample_progress":
            job["current_system"] = event["system"]
            job["progress"][event["system"]] = {
                "completed_samples": event["completed_samples"],
                "total_samples": event["total_samples"],
            }
        elif event_type == "system_completed":
            job["partial_metrics"][event["system"]] = event["metrics"]
        elif event_type == "completed":
            job["status"] = "completed"
            job["result"] = event["result"]
        elif event_type == "failed":
            job["status"] = "failed"
            job["error"] = event["error"]

    process.join(timeout=0.1)
    job = eval_jobs.get(job_id)
    if job and job["status"] == "running":
        job["status"] = "completed" if "result" in job else "failed"


def start_eval_job(dataset_path: str) -> dict:
    job_id = f"eval_{uuid4().hex[:8]}"
    queue: Queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_run_eval_worker,
        args=(job_id, dataset_path, queue),
        daemon=True,
    )
    eval_jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "dataset_path": dataset_path,
        "current_system": None,
        "partial_metrics": {},
        "progress": {
            "stacked_multi_agent": {"completed_samples": 0, "total_samples": 0},
            "baseline_single_agent": {"completed_samples": 0, "total_samples": 0},
        },
    }
    process.start()
    consumer = Thread(target=_consume_eval_queue, args=(job_id, queue, process), daemon=True)
    consumer.start()
    return eval_jobs[job_id]


def get_eval_job(job_id: str) -> dict:
    return eval_jobs[job_id]


def get_eval_result(job_id: str) -> dict:
    return eval_jobs[job_id]["result"]
