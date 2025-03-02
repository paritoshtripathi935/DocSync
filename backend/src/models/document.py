from pydantic import BaseModel
from typing import List, Optional


class Document(BaseModel):
    id: int
    title: str
    content: str
    version: int
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
        table = 'documents'