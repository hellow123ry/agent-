from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.eval import EvalJobResponse, EvalRunRequest
from app.services.eval_service import get_eval_job, get_eval_result, start_eval_job


router = APIRouter()


@router.post("/run", response_model=EvalJobResponse)
def run_eval_job(payload: EvalRunRequest) -> EvalJobResponse:
    job = start_eval_job(payload.dataset_path)
    return EvalJobResponse(job_id=job["job_id"], status=job["status"])


@router.get("/jobs/{job_id}")
def get_eval_job_route(job_id: str) -> dict:
    try:
        return get_eval_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@router.get("/jobs/{job_id}/result")
def get_eval_result_route(job_id: str) -> dict:
    try:
        return get_eval_result(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc
