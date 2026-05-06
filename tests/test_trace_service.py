from app.services.trace_service import TraceCollector, trace_collector_context


def test_trace_collector_records_tool_call():
    collector = TraceCollector()
    collector.record("tool_call", {"tool_name": "search_hotels"})

    assert len(collector.events) == 1
    assert collector.events[0]["type"] == "tool_call"
    assert collector.events[0]["payload"]["tool_name"] == "search_hotels"


def test_trace_collector_context_registers_active_collector():
    collector = TraceCollector()

    with trace_collector_context(collector):
        collector.record("router", {"intent": "hotel"})

    assert collector.events[0]["payload"]["intent"] == "hotel"
