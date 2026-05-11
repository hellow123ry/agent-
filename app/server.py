from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.env import load_project_env
from app.api.chat import router as chat_router
from app.api.eval import router as eval_router
from app.api.knowledgebase import router as knowledgebase_router
from app.api.reports import router as reports_router


load_project_env()

app = FastAPI(title="Multi Agent Dialog Workbench")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(eval_router, prefix="/api/eval", tags=["eval"])
app.include_router(knowledgebase_router, prefix="/api/knowledgebase", tags=["knowledgebase"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
