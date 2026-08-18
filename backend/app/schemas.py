"""
Pydantic schemas - request/respinse validation for docs
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Payload for creating new documents
class DocCreate(BaseModel):

    title: str = Field(..., min_length = 1, max_length = 255)
    content: str = Field(..., min_length = 1)

# Document as returned by the API
class DocResponse(BaseModel):

    model_config = ConfigDict(from_attributes = True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

# Payload for POST /api/chat
class ChatRequest(BaseModel):
    message: str = Field(..., min_length = 1, max_length = 2000)

# A single retrieved document, returned alongside the answer
class Source(BaseModel):
    title: str
    content: str

# Response for POST /api/chat
class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
