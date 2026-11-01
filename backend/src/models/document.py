from pydantic import BaseModel
from typing import List, Optional, Dict


class Document(BaseModel):
    id: Optional[int] = None  # assigned by the server when omitted
    title: str
    content: str = ""
    version: int = 1
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentList(BaseModel):
    items: List[Document]
    total: int
    skip: int
    limit: int