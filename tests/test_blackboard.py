from multi_agent_dialog.experts import dining_expert, hotel_expert
from multi_agent_dialog.state import DialogState
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

@patch("multi_agent_dialog.experts.get_llm")
def test_expert_uses_blackboard(mock_get_llm):
    # 测试专家是否能读取黑板上的信息
    mock_llm = MagicMock()
    mock_llm_with_tools = MagicMock()
    # 模拟大模型直接回答，不再追问人数，因为它从黑板读到了
    mock_response = AIMessage(content="为您查到北京的烤肉店...")
    mock_llm_with_tools.invoke.return_value = mock_response
    mock_llm.bind_tools.return_value = mock_llm_with_tools
    mock_get_llm.return_value = mock_llm

    # 初始化状态时，黑板上已经有 "北京" 和 3 个人
    state = DialogState(
        messages=[HumanMessage(content="订个烤肉店")], 
        task_stack=[], 
        active_task="dining", 
        current_intent="dining",
        global_blackboard={"location": "北京", "people_count": 3}
    )
    
    result = dining_expert(state)
    
    # 验证大模型的提示词中是否成功注入了黑板信息
    call_messages = mock_llm_with_tools.invoke.call_args[0][0]
    system_prompt = call_messages[0].content
    assert "北京" in system_prompt
    assert "3" in system_prompt