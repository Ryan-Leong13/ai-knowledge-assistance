"""
AI Knowledge Assistance - FastAPI backend entrypoint

Run using:
    uvicorn backend.app.main:app --reload
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from backend.app.database import Base, engine
from backend.app.routers import documents, chat

load_dotenv()

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_knowledge_assistant")

Base.metadata.create_all(bind = engine)

app = FastAPI(
    title = "AI Knowledge Assistance",
    description = "RAG-based Q&A over a company knowledge base",
    version = "0.1.0",
)

app.include_router(documents.router)
app.include_router(chat.router)

# Frontend: served from the sibling "frontend/" directory to keep 
# physically separate from "backend/" for a clean architectural boundary
frontEnd_DIR = Path(__file__).resolve().parents[2] / "frontend"
templates = Jinja2Templates(directory = str(frontEnd_DIR / "templates"))
app.mount("/static", StaticFiles(directory = str (frontEnd_DIR / "static")), name = "static")


@app.get("/health")
def health_check():
    logger.info("Health check hit")
    return {"status" : "ok"}

# Serve the chat interface
@app.get("/")
def chat_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})