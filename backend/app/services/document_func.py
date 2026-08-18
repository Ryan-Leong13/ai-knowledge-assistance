"""
Document CRUD Service - plain data access function
Kept separate form the API routers so this logic is easy to unit test 
and easy to reuse from the seed script
"""

import logging
from sqlalchemy.orm import Session
from backend.app.models import Document

logger = logging.getLogger("ai_knowledge_assistant")

# Insert a new document and return it
def create_doc(db: Session, title: str, content: str) -> Document:
    doc = Document(title = title, content = content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info("Created document id = %s title = %r", doc.id, doc.title)

    return doc

# Fetch a single document by id, or None if it doesn't exist
def get_doc(db: Session, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()

# Return all documents, most recently created first
def list_doc(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()

# Delete a document by its id
# If document was deleted, return True. If document doesn't exist, return False
def dlt_doc(db: Session, document_id: int) -> bool:
    doc = get_doc(db, document_id)

    if doc is None:
        return False

    db.delete(doc)
    db.commit()
    logger.info("Deleted document id=%s", document_id)

    return True