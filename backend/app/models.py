"""
SQLAlchemy models for the knowledge base
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from backend.app.database import Base

# A single knowledge base document
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(255), nullable = False, index = True)
    content = Column(Text, nullable = False)
    embedding = Column(LargeBinary, nullable = True)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default = lambda: datetime.now(timezone.utc),
        onupdate = lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Document id = {self.id} title = {self.title!r}>"