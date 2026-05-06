from multi_agent_dialog.router import route_intent
from multi_agent_dialog.state import DialogState
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from app.services.trace_service import TraceCollector, trace_collector_context

@patch("multi_agent_dialog.router.get_llm")
def test_router_dining(mock_get_llm):
    # Mock LLM 返回
    mock_llm = MagicMock()
    mock_response = AIMessage(content="dining")
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="订个烤肉店")], task_stack=[], active_task="", current_intent="", global_blackboard={})
    result = route_intent(state)
    assert result["current_intent"] == "dining"

@patch("multi_agent_dialog.router.get_llm")
def test_router_travel(mock_get_llm):
    mock_llm = MagicMock()
    mock_response = AIMessage(content="travel")
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="帮我打个车")], task_stack=[], active_task="", current_intent="", global_blackboard={})
    result = route_intent(state)
    assert result["current_intent"] == "travel"


@patch("multi_agent_dialog.router.get_llm")
def test_router_emits_trace(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="hotel")
    mock_get_llm.return_value = mock_llm
    collector = TraceCollector()
    state = DialogState(
        messages=[HumanMessage(content="帮我查酒店")],
        task_stack=[],
        active_task="",
        current_intent="",
        global_blackboard={},
    )

    with trace_collector_context(collector):
        result = route_intent(state)

    assert result["current_intent"] == "hotel"
    assert any(event["type"] == "router" for event in collector.events)
