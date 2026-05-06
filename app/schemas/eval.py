from __future__ import annotations

from pydantic import BaseModel


class EvalRunRequest(BaseModel):
    dataset_path: str


class EvalJobResponse(BaseModel):
    job_id: str
    status: str
