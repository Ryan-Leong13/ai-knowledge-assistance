"""
Chat API route

    POST /api/chat
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import ChatRequest, ChatResponse
from backend.app.services import rag_func

logger = logging.getLogger("ai_knowledge_assistant")

router = APIRouter(prefix = "/api", tags = ["chat"])


# Answer a user's question using RAG over KB.
# Returns the generated answer plus the source document used to construct it
@router.post("/chat", response_model = ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    logger.info("Chat request received: %r.", payload.message)

    try:
        result = rag_func.answer_question(db, payload.message)
    except Exception:
        logger.exception("Failed to answer chat query: %r", payload.message)
        raise HTTPException(
            status_code = 502,
            detail = (
                "The AI assistant is currently unavailable. Please confirm "
                "the LLM service (Ollama) is running and try again."
            ),
        )

    return result