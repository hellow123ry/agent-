from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import uuid4


_active_collector: ContextVar["TraceCollector | None"] = ContextVar(
    "active_trace_collector", default=None
)


class TraceCollector:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, event_type: str, payload: dict, latency_ms: int | None = None) -> None:
        event = {
            "id": f"trace_{uuid4().hex[:8]}",
            "type": event_type,
            "timestamp": time.time(),
            "payload": payload,
        }
        if latency_ms is not None:
            event["latency_ms"] = latency_ms
        self.events.append(event)


def get_active_trace_collector() -> TraceCollector | None:
    return _active_collector.get()


@contextmanager
def trace_collector_context(collector: TraceCollector):
    token = _active_collector.set(collector)
    try:
        yield collector
    finally:
        _active_collector.reset(token)
