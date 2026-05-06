from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.knowledgebase import EnvelopeResponse, HotelsUpdateRequest, RestaurantsUpdateRequest
from app.services.knowledgebase_service import (
    KnowledgebaseValidationError,
    load_knowledgebase,
    update_hotels,
    update_restaurants,
)


router = APIRouter()


def _success(data: dict) -> EnvelopeResponse:
    return EnvelopeResponse(ok=True, data=data)


def _validation_error_response(exc: KnowledgebaseValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "ok": False,
            "error": {
                "code": "validation_error",
                "message": str(exc),
                "field": exc.field,
            },
        },
    )


@router.get("", response_model=EnvelopeResponse)
def get_knowledgebase() -> EnvelopeResponse:
    return _success(load_knowledgebase())


@router.put("/restaurants", response_model=EnvelopeResponse)
def put_restaurants(payload: RestaurantsUpdateRequest):
    try:
        updated = update_restaurants([item.model_dump() for item in payload.restaurants])
    except KnowledgebaseValidationError as exc:
        return _validation_error_response(exc)
    return _success(updated)


@router.put("/hotels", response_model=EnvelopeResponse)
def put_hotels(payload: HotelsUpdateRequest):
    try:
        updated = update_hotels([item.model_dump() for item in payload.hotels])
    except KnowledgebaseValidationError as exc:
        return _validation_error_response(exc)
    return _success(updated)
