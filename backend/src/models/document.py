from pydantic import BaseModel
from typing import List, Optional, Dict


class Document(BaseModel):
    id: int
    title: str
    content: str
    version: int
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class DocumentList(BaseModel):
    items: List[Document]
    total: int
    skip: int
    limit: int