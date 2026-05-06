from typing import TypedDict, List, Tuple, Dict, Any
from langchain_core.messages import BaseMessage

class DialogState(TypedDict):
    messages: List[BaseMessage]
    task_stack: List[str]
    active_task: str
    current_intent: str
    global_blackboard: Dict[str, Any]
    knowledgebase: Dict[str, Any]

def push_task(state: DialogState, task_name: str) -> DialogState:
    new_stack = state.get("task_stack", []).copy()
    if task_name and task_name not in new_stack:
        new_stack.append(task_name)
    return {**state, "task_stack": new_stack}

def pop_task(state: DialogState) -> Tuple[DialogState, str]:
    new_stack = state.get("task_stack", []).copy()
    if not new_stack:
        return state, ""
    popped = new_stack.pop()
    return {**state, "task_stack": new_stack}, popped
