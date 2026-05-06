from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.services.knowledgebase_service import load_knowledgebase
from multi_agent_dialog.experts import (
    default_expert,
    dining_expert,
    entertainment_expert,
    hotel_expert,
    travel_expert,
)
from multi_agent_dialog.graph import run_dialog
from multi_agent_dialog.router import route_intent
from multi_agent_dialog.state import DialogState


def build_state(use_stack: bool = True, use_blackboard: bool = True) -> DialogState:
    return DialogState(
        messages=[],
        task_stack=[] if use_stack else [],
        active_task="",
        current_intent="",
        global_blackboard={} if use_blackboard else {},
        knowledgebase=load_knowledgebase(),
    )


def _select_expert(intent: str):
    if intent == "dining":
        return dining_expert
    if intent == "hotel":
        return hotel_expert
    if intent == "travel":
        return travel_expert
    if intent == "entertainment":
        return entertainment_expert
    return default_expert


def run_baseline_dialog(initial_state: DialogState) -> DialogState:
    baseline_state = {
        **initial_state,
        "task_stack": [],
        "active_task": "",
        "global_blackboard": {},
    }
    routed_state = route_intent(baseline_state)
    expert = _select_expert(routed_state.get("current_intent", "unknown"))
    result_state = expert(
        {
            **routed_state,
            "task_stack": [],
            "active_task": routed_state.get("current_intent", ""),
            "global_blackboard": {},
        }
    )
    result_state["task_stack"] = []
    result_state["global_blackboard"] = {}
    return result_state


def run_system_turns(
    system_name: str, state: DialogState, user_turns: list[str]
) -> DialogState:
    current_state = state
    for turn in user_turns:
        current_state["messages"].append(HumanMessage(content=turn))
        if system_name == "baseline_single_agent":
            current_state = run_baseline_dialog(current_state)
        else:
            current_state = run_dialog(current_state)
    return current_state
