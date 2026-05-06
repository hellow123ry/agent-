from __future__ import annotations

import mimetypes

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.services.report_service import (
    get_latest_report,
    list_report_history,
    resolve_report_file,
)


router = APIRouter()


@router.get("/latest")
def get_latest_report_route() -> dict:
    return get_latest_report()


@router.get("/history")
def get_report_history() -> dict:
    return {"items": list_report_history()}


@router.get("/file")
def get_report_file(path: str = Query(..., description="relative path under evaluation/results")):
    try:
        resolved = resolve_report_file(path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid report path") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="report file not found") from exc

    media_type, _ = mimetypes.guess_type(str(resolved))
    return FileResponse(path=str(resolved), media_type=media_type or "application/octet-stream")
