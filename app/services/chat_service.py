from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.state.session_store import chat_sessions
from app.services.knowledgebase_service import load_knowledgebase
from app.services.trace_service import TraceCollector, trace_collector_context
from multi_agent_dialog.graph import run_dialog
from multi_agent_dialog.state import DialogState


def _build_empty_state() -> DialogState:
    return DialogState(
        messages=[],
        task_stack=[],
        active_task="",
        current_intent="",
        global_blackboard={},
        knowledgebase=load_knowledgebase(),
    )


def _serialize_message(message) -> dict:
    if isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content, "message_type": "HumanMessage"}
    if isinstance(message, ToolMessage):
        return {"role": "tool", "content": message.content, "message_type": "ToolMessage"}
    if isinstance(message, AIMessage):
        return {"role": "assistant", "content": message.content, "message_type": "AIMessage"}
    if isinstance(message, BaseMessage):
        return {
            "role": message.type,
            "content": message.content,
            "message_type": message.__class__.__name__,
        }
    if isinstance(message, dict):
        return {
            "role": "assistant" if message.get("type") == "ai" else "user",
            "content": message.get("content", ""),
            "message_type": message.get("type", "dict"),
        }
    return {"role": "unknown", "content": str(message), "message_type": type(message).__name__}


def _serialize_state(state: dict) -> dict:
    return {
        "current_intent": state.get("current_intent", ""),
        "active_task": state.get("active_task", ""),
        "task_stack": list(state.get("task_stack", [])),
        "global_blackboard": dict(state.get("global_blackboard", {})),
    }


def create_session() -> dict:
    session_id = f"sess_{uuid4().hex[:8]}"
    state = _build_empty_state()
    chat_sessions[session_id] = state
    return {
        "session_id": session_id,
        "messages": [],
        "state": _serialize_state(state),
    }


def get_session(session_id: str) -> dict:
    state = chat_sessions[session_id]
    return {
        "session_id": session_id,
        "messages": [_serialize_message(message) for message in state.get("messages", [])],
        "state": _serialize_state(state),
    }


def reset_session(session_id: str) -> dict:
    state = _build_empty_state()
    chat_sessions[session_id] = state
    return {
        "session_id": session_id,
        "messages": [],
        "state": _serialize_state(state),
    }


def run_turn(session_id: str, message: str) -> dict:
    state = deepcopy(chat_sessions[session_id])
    state["messages"].append(HumanMessage(content=message))
    collector = TraceCollector()
    with trace_collector_context(collector):
        updated_state = run_dialog(state)
    chat_sessions[session_id] = updated_state
    return {
        "session_id": session_id,
        "messages": [_serialize_message(item) for item in updated_state.get("messages", [])],
        "state": _serialize_state(updated_state),
        "traces": collector.events,
    }
