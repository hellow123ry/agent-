import json
import os
from pathlib import Path

import pytest

from app.services import knowledgebase_service


def test_load_knowledgebase_initializes_missing_file(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)

    data = knowledgebase_service.load_knowledgebase()

    assert knowledgebase_path.exists()
    assert data["restaurants"]
    assert data["hotels"]
    assert json.loads(knowledgebase_path.read_text(encoding="utf-8")) == data


def test_save_knowledgebase_uses_atomic_replace(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    replace_calls: list[tuple[Path, Path]] = []
    real_replace = os.replace

    def tracked_replace(src: str, dst: str) -> None:
        replace_calls.append((Path(src), Path(dst)))
        real_replace(src, dst)

    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)
    monkeypatch.setattr(knowledgebase_service.os, "replace", tracked_replace)

    payload = {
        "restaurants": [
            {
                "name": "测试餐厅",
                "type": "火锅",
                "capacity": [2, 4],
                "status": "有位",
            }
        ],
        "hotels": [
            {
                "name": "测试酒店",
                "location": "市中心",
                "type": "商务",
                "price": 699,
                "status": "有房",
            }
        ],
    }

    saved = knowledgebase_service.save_knowledgebase(payload)

    assert saved == payload
    assert json.loads(knowledgebase_path.read_text(encoding="utf-8")) == payload
    assert len(replace_calls) == 1
    assert replace_calls[0][1] == knowledgebase_path
    assert not replace_calls[0][0].exists()


def test_save_knowledgebase_validates_restaurants_and_hotels(tmp_path, monkeypatch):
    knowledgebase_path = tmp_path / "knowledgebase.json"
    monkeypatch.setattr(knowledgebase_service, "KNOWLEDGEBASE_PATH", knowledgebase_path)

    with pytest.raises(knowledgebase_service.KnowledgebaseValidationError) as restaurant_error:
        knowledgebase_service.save_knowledgebase(
            {
                "restaurants": [
                    {
                        "name": "坏数据餐厅",
                        "type": "火锅",
                        "capacity": [0],
                        "status": "有位",
                    }
                ],
                "hotels": [],
            }
        )

    assert restaurant_error.value.field == "restaurants[0].capacity"

    with pytest.raises(knowledgebase_service.KnowledgebaseValidationError) as hotel_error:
        knowledgebase_service.save_knowledgebase(
            {
                "restaurants": [],
                "hotels": [
                    {
                        "name": "坏数据酒店",
                        "location": "市中心",
                        "type": "商务",
                        "price": -1,
                        "status": "有房",
                    }
                ],
            }
        )

    assert hotel_error.value.field == "hotels[0].price"
