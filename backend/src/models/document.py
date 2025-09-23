from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import json

class DocumentBase(BaseModel):
    title: str
    content: str
    chunk_id: str
    embedding: Optional[List[float]] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_at: datetime
    
    @field_validator('embedding', mode='before')
    @classmethod
    def parse_embedding(cls, v):
        if isinstance(v, str):
            try:
                # Convert string representation of list to actual list
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[str]