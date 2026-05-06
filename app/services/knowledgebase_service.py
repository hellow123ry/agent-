from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGEBASE_PATH = PROJECT_ROOT / "data" / "knowledgebase.json"

DEFAULT_KNOWLEDGEBASE = {
    "restaurants": [
        {"name": "全聚德烤鸭", "type": "烤肉店/烤鸭", "capacity": [2, 3, 4, 6, 8], "status": "有位"},
        {"name": "海底捞火锅", "type": "火锅", "capacity": [2, 4, 6], "status": "爆满"},
        {"name": "汉拿山韩式烤肉", "type": "烤肉店", "capacity": [2, 3, 4], "status": "有位"},
    ],
    "hotels": [
        {"name": "希尔顿酒店", "location": "市中心", "type": "豪华", "price": 1200, "status": "有房"},
        {"name": "如家快捷酒店", "location": "火车站", "type": "经济", "price": 300, "status": "有房"},
        {"name": "桔子水晶酒店", "location": "市中心", "type": "舒适", "price": 600, "status": "满房"},
    ],
}


class KnowledgebaseValidationError(ValueError):
    def __init__(self, message: str, *, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.field = field


def _ensure_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgebaseValidationError(f"{field} must be a non-empty string", field=field)
    return value.strip()


def _validate_restaurant(item: dict[str, Any], index: int) -> dict[str, Any]:
    field_prefix = f"restaurants[{index}]"
    capacity = item.get("capacity")
    if not isinstance(capacity, list) or not capacity:
        raise KnowledgebaseValidationError("restaurant capacity must be a non-empty list", field=f"{field_prefix}.capacity")
    if any(not isinstance(seat, int) or seat <= 0 for seat in capacity):
        raise KnowledgebaseValidationError("restaurant capacity must contain positive integers", field=f"{field_prefix}.capacity")
    return {
        "name": _ensure_non_empty_string(item.get("name"), f"{field_prefix}.name"),
        "type": _ensure_non_empty_string(item.get("type"), f"{field_prefix}.type"),
        "capacity": capacity,
        "status": _ensure_non_empty_string(item.get("status"), f"{field_prefix}.status"),
    }


def _validate_hotel(item: dict[str, Any], index: int) -> dict[str, Any]:
    field_prefix = f"hotels[{index}]"
    price = item.get("price")
    if not isinstance(price, int) or price < 0:
        raise KnowledgebaseValidationError("hotel price must be a non-negative integer", field=f"{field_prefix}.price")
    return {
        "name": _ensure_non_empty_string(item.get("name"), f"{field_prefix}.name"),
        "location": _ensure_non_empty_string(item.get("location"), f"{field_prefix}.location"),
        "type": _ensure_non_empty_string(item.get("type"), f"{field_prefix}.type"),
        "price": price,
        "status": _ensure_non_empty_string(item.get("status"), f"{field_prefix}.status"),
    }


def validate_knowledgebase(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    restaurants = payload.get("restaurants")
    hotels = payload.get("hotels")
    if not isinstance(restaurants, list):
        raise KnowledgebaseValidationError("restaurants must be a list", field="restaurants")
    if not isinstance(hotels, list):
        raise KnowledgebaseValidationError("hotels must be a list", field="hotels")
    return {
        "restaurants": [_validate_restaurant(item, index) for index, item in enumerate(restaurants)],
        "hotels": [_validate_hotel(item, index) for index, item in enumerate(hotels)],
    }


def _atomic_write(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_path = Path(handle.name)
    os.replace(str(temp_path), str(path))


def load_knowledgebase(path: Optional[Path] = None) -> dict[str, list[dict[str, Any]]]:
    target_path = path or KNOWLEDGEBASE_PATH
    if not target_path.exists():
        payload = deepcopy(DEFAULT_KNOWLEDGEBASE)
        _atomic_write(payload, target_path)
        return payload
    with target_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_knowledgebase(payload)


def save_knowledgebase(payload: dict[str, Any], path: Optional[Path] = None) -> dict[str, list[dict[str, Any]]]:
    target_path = path or KNOWLEDGEBASE_PATH
    validated = validate_knowledgebase(payload)
    _atomic_write(validated, target_path)
    return validated


def update_restaurants(restaurants: list[dict[str, Any]], path: Optional[Path] = None) -> dict[str, list[dict[str, Any]]]:
    current = load_knowledgebase(path)
    current["restaurants"] = restaurants
    return save_knowledgebase(current, path)


def update_hotels(hotels: list[dict[str, Any]], path: Optional[Path] = None) -> dict[str, list[dict[str, Any]]]:
    current = load_knowledgebase(path)
    current["hotels"] = hotels
    return save_knowledgebase(current, path)
