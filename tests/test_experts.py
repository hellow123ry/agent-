from multi_agent_dialog.experts import (
    _execute_tool_call,
    _run_tool_call_loop,
    dining_expert,
    entertainment_expert,
    hotel_expert,
    travel_expert,
)
from multi_agent_dialog.state import DialogState
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from app.services.trace_service import TraceCollector, trace_collector_context
import json

@patch("multi_agent_dialog.experts.get_llm")
def test_dining_expert(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm_with_tools = MagicMock()
    mock_response = AIMessage(content="好的，我来帮您预订餐厅。请问您想吃什么类型的餐厅？")
    mock_llm_with_tools.invoke.return_value = mock_response
    mock_llm.bind_tools.return_value = mock_llm_with_tools
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="我想订个餐厅")], task_stack=[], active_task="", current_intent="dining", global_blackboard={})
    result = dining_expert(state)
    assert "餐厅" in result["messages"][-1].content

@patch("multi_agent_dialog.experts.get_llm")
def test_hotel_expert(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm_with_tools = MagicMock()
    mock_response = AIMessage(content="没问题，正在为您查询酒店。请问入住时间是？")
    mock_llm_with_tools.invoke.return_value = mock_response
    mock_llm.bind_tools.return_value = mock_llm_with_tools
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="帮我查下酒店")], task_stack=[], active_task="", current_intent="hotel", global_blackboard={})
    result = hotel_expert(state)
    assert "酒店" in result["messages"][-1].content


@patch("multi_agent_dialog.experts.get_llm")
def test_hotel_expert_handles_multi_round_tool_calls(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm_with_tools = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools
    mock_get_llm.return_value = mock_llm

    first_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "update_blackboard",
                "args": {"location": "北京", "date": "明天"},
                "id": "call_1",
                "type": "tool_call",
            }
        ],
    )
    second_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_hotels",
                "args": {"location": "北京", "hotel_type": ""},
                "id": "call_2",
                "type": "tool_call",
            }
        ],
    )
    final_response = AIMessage(content="为您查到了北京的酒店。")
    mock_llm_with_tools.invoke.side_effect = [
        first_response,
        second_response,
        final_response,
    ]

    state = DialogState(
        messages=[HumanMessage(content="我在北京，帮我看看明天的酒店")],
        task_stack=[],
        active_task="",
        current_intent="hotel",
        global_blackboard={},
    )
    result = hotel_expert(state)

    assert result["messages"][-1].content == "为您查到了北京的酒店。"
    assert result["global_blackboard"]["location"] == "北京"
    assert result["global_blackboard"]["date"] == "明天"


def test_run_tool_call_loop_stops_after_max_rounds():
    mock_llm_with_tools = MagicMock()
    first_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_hotels",
                "args": {"location": "", "hotel_type": ""},
                "id": "call_1",
                "type": "tool_call",
            }
        ],
    )
    second_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_hotels",
                "args": {"location": "", "hotel_type": ""},
                "id": "call_2",
                "type": "tool_call",
            }
        ],
    )
    mock_llm_with_tools.invoke.return_value = second_response
    state = DialogState(
        messages=[HumanMessage(content="查酒店")],
        task_stack=[],
        active_task="hotel",
        current_intent="hotel",
        global_blackboard={},
    )

    new_state, response, _ = _run_tool_call_loop(
        mock_llm_with_tools,
        state,
        [SystemMessage(content="system"), HumanMessage(content="查酒店")],
        first_response,
        max_tool_rounds=1,
    )

    assert "工具调用" in response.content
    assert "过多" in response.content
    assert new_state["messages"][-1].content == response.content
    assert mock_llm_with_tools.invoke.call_count == 1


def test_run_tool_call_loop_emits_tool_trace():
    mock_llm_with_tools = MagicMock()
    first_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_hotels",
                "args": {"location": "", "hotel_type": ""},
                "id": "call_1",
                "type": "tool_call",
            }
        ],
    )
    final_response = AIMessage(content="已查询完成。")
    mock_llm_with_tools.invoke.return_value = final_response
    collector = TraceCollector()
    state = DialogState(
        messages=[HumanMessage(content="查酒店")],
        task_stack=[],
        active_task="hotel",
        current_intent="hotel",
        global_blackboard={},
    )

    with trace_collector_context(collector):
        _run_tool_call_loop(
            mock_llm_with_tools,
            state,
            [SystemMessage(content="system"), HumanMessage(content="查酒店")],
            first_response,
        )

    event_types = [event["type"] for event in collector.events]
    assert "tool_call" in event_types
    assert "tool_result" in event_types


def test_execute_tool_call_uses_knowledgebase_snapshot():
    state = DialogState(
        messages=[HumanMessage(content="查酒店")],
        task_stack=[],
        active_task="hotel",
        current_intent="hotel",
        global_blackboard={},
        knowledgebase={
            "restaurants": [],
            "hotels": [
                {
                    "name": "知识库酒店",
                    "location": "望京",
                    "type": "经济",
                    "price": 299,
                    "status": "有房",
                }
            ],
        },
    )

    tool_message = _execute_tool_call(
        {
            "name": "search_hotels",
            "args": {"location": "望京", "hotel_type": "经济"},
            "id": "call_1",
            "type": "tool_call",
        },
        state,
    )

    payload = json.loads(tool_message.content)
    assert payload["status"] == "success"
    assert "知识库酒店" in payload["hotels"][0]


@patch("multi_agent_dialog.experts.get_llm")
def test_travel_expert(mock_get_llm):
    mock_llm = MagicMock()
    mock_response = AIMessage(content="没问题，请问您的出发地和目的地是哪里？")
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="帮我买张去北京的高铁票")], task_stack=[], active_task="", current_intent="travel", global_blackboard={})
    result = travel_expert(state)
    assert "目的地" in result["messages"][-1].content

@patch("multi_agent_dialog.experts.get_llm")
def test_entertainment_expert(mock_get_llm):
    mock_llm = MagicMock()
    mock_response = AIMessage(content="好的，请问您想看什么类型的电影？")
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    state = DialogState(messages=[HumanMessage(content="周末想看电影")], task_stack=[], active_task="", current_intent="entertainment", global_blackboard={})
    result = entertainment_expert(state)
    assert "电影" in result["messages"][-1].content
