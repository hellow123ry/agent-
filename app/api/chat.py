from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatSessionResponse, ChatTurnRequest, ChatTurnResponse
from app.services.chat_service import create_session, get_session, reset_session, run_turn


router = APIRouter()


@router.post("/session", response_model=ChatSessionResponse)
def create_chat_session() -> ChatSessionResponse:
    return ChatSessionResponse(**create_session())


@router.get("/session/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: str) -> ChatSessionResponse:
    try:
        return ChatSessionResponse(**get_session(session_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc


@router.delete("/session/{session_id}", response_model=ChatSessionResponse)
def delete_chat_session(session_id: str) -> ChatSessionResponse:
    return ChatSessionResponse(**reset_session(session_id))


@router.post("/session/{session_id}/turn", response_model=ChatTurnResponse)
def create_chat_turn(session_id: str, payload: ChatTurnRequest) -> ChatTurnResponse:
    try:
        return ChatTurnResponse(**run_turn(session_id, payload.message))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
