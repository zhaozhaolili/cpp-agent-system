from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    sources: List[str] = []
    created_at: str

    class Config:
        from_attributes = True
