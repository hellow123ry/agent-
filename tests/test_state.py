import pytest
from multi_agent_dialog.state import DialogState, push_task, pop_task
from langchain_core.messages import HumanMessage

def test_push_and_pop_task():
    state = DialogState(messages=[HumanMessage(content="订个餐厅")], task_stack=[], current_intent="dining")
    
    state1 = push_task(state, "hotel")
    assert state1["task_stack"] == ["hotel"]
    
    state2, popped = pop_task(state1)
    assert popped == "hotel"
    assert len(state2["task_stack"]) == 0
