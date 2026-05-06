from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class RestaurantRecord(BaseModel):
    name: str
    type: str
    capacity: list[int] = Field(default_factory=list)
    status: str


class HotelRecord(BaseModel):
    name: str
    location: str
    type: str
    price: int
    status: str


class KnowledgebasePayload(BaseModel):
    restaurants: list[RestaurantRecord] = Field(default_factory=list)
    hotels: list[HotelRecord] = Field(default_factory=list)


class RestaurantsUpdateRequest(BaseModel):
    restaurants: list[RestaurantRecord] = Field(default_factory=list)


class HotelsUpdateRequest(BaseModel):
    hotels: list[HotelRecord] = Field(default_factory=list)


class ErrorPayload(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class EnvelopeResponse(BaseModel):
    ok: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[ErrorPayload] = None
