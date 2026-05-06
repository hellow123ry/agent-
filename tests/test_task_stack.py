from multi_agent_dialog.state import DialogState
from multi_agent_dialog.router import route_intent
from multi_agent_dialog.experts import _handle_task_completion
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

@patch("multi_agent_dialog.router.get_llm")
def test_router_push_task(mock_get_llm):
    # Mock LLM 返回新意图
    mock_llm = MagicMock()
    mock_response = AIMessage(content="hotel")
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    # 初始状态：正在进行 dining
    state = DialogState(
        messages=[HumanMessage(content="订个酒店")], 
        task_stack=[], 
        active_task="dining", 
        current_intent="dining"
    )
    
    result = route_intent(state)
    
    # 验证是否发生了压栈
    assert result["current_intent"] == "hotel"
    assert result["active_task"] == "hotel"
    assert "dining" in result["task_stack"]

@patch("multi_agent_dialog.experts.get_llm")
def test_expert_pop_task(mock_get_llm):
    # Mock 恢复话题时的生成
    mock_llm = MagicMock()
    mock_response = AIMessage(content="顺便说一句，您之前的餐厅需要几点？")
    mock_llm.invoke.return_value = mock_response

    state = DialogState(
        messages=[],
        task_stack=["dining"],
        active_task="hotel",
        current_intent="hotel"
    )
    
    base_messages = []
    original_content = "酒店为您预订成功！[TASK_COMPLETED]"
    clean_content = "酒店为您预订成功！"
    
    new_state, updated_response = _handle_task_completion(state, mock_llm, base_messages, clean_content)
    
    # 验证是否发生弹栈并切回 dining
    assert new_state["active_task"] == "dining"
    assert len(new_state["task_stack"]) == 0
    assert "顺便说一句" in updated_response.content
    assert "酒店为您预订成功！" in updated_response.content