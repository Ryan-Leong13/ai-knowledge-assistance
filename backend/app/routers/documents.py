"""
Document management API routes

    GET /api/documents      -> list all documents
    POST /api/documents     -> create a new document
    DELETE /api/documents   -> Delete a document by document id
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import DocCreate, DocResponse
from backend.app.services import document_func

logger = logging.getLogger("ai_knowledge_assistance")

router = APIRouter(prefix = "/api/documents", tags = ["documents"])

@router.get("", response_model = list[DocResponse])
# Return all documents in KB
def list_doc(db: Session = Depends(get_db)):
    return document_func.list_doc(db)

@router.post("", response_model = DocResponse, status_code = 201)
# Create new document
# Note: This does not compute an embedding yet, it will be retrievable 
# by the chat endpoint until re-embedded
def create_do(payload: DocCreate, db: Session = Depends(get_db)):
    doc = document_func.create_doc(
        db, title = payload.title, content = payload.content
    )
    return doc

@router.delete("/{document_id}", status_code = 204)
# Delete a document by id. Return 404 if file doesn't exist
def delete_doc(document_id: int, db: Session = Depends(get_db)):
    deleted = document_func.dlt_doc(db, document_id)

    if not deleted:
        logger.warning("Delete requested for missing document id=%s", document_id)
        raise HTTPException(status_code = 404, detail = "Document not found")

    return None