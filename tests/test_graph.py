from multi_agent_dialog.graph import run_dialog
from multi_agent_dialog.state import DialogState
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

@patch("multi_agent_dialog.experts.get_llm")
@patch("multi_agent_dialog.router.get_llm")
def test_graph_flow(mock_router_llm, mock_experts_llm):
    # Mock Router LLM
    mock_router_response = AIMessage(content="hotel")
    mock_router_llm.return_value.invoke.return_value = mock_router_response

    # Mock Experts LLM (with tools)
    mock_experts_response = AIMessage(content="没问题，正在为您查询酒店。请问入住时间是？")
    mock_llm_with_tools = MagicMock()
    mock_llm_with_tools.invoke.return_value = mock_experts_response
    mock_experts_llm.return_value.bind_tools.return_value = mock_llm_with_tools

    state = DialogState(messages=[HumanMessage(content="帮我查下酒店")], task_stack=[], active_task="", current_intent="", global_blackboard={})
    final_state = run_dialog(state)
    assert "酒店" in final_state["messages"][-1].content

@patch("multi_agent_dialog.experts.get_llm")
@patch("multi_agent_dialog.router.get_llm")
def test_graph_flow_default(mock_router_llm, mock_experts_llm):
    # Mock Router LLM returning unknown
    mock_router_response = AIMessage(content="unknown")
    mock_router_llm.return_value.invoke.return_value = mock_router_response

    # Mock Default Expert LLM
    mock_experts_response = AIMessage(content="您好！我是一个生活服务助手，可以帮您预订酒店和餐厅。")
    mock_experts_llm.return_value.invoke.return_value = mock_experts_response

    state = DialogState(messages=[HumanMessage(content="你能做什么")], task_stack=[], active_task="", current_intent="", global_blackboard={})
    final_state = run_dialog(state)
    assert "助手" in final_state["messages"][-1].content
