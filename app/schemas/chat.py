from __future__ import annotations

from pydantic import BaseModel


class ChatStateResponse(BaseModel):
    current_intent: str = ""
    active_task: str = ""
    task_stack: list[str] = []
    global_blackboard: dict = {}


class ChatSessionResponse(BaseModel):
    session_id: str
    messages: list[dict]
    state: ChatStateResponse


class ChatTurnRequest(BaseModel):
    message: str


class ChatTurnResponse(BaseModel):
    session_id: str
    messages: list[dict]
    state: ChatStateResponse
    traces: list[dict] = []

