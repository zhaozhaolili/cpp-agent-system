# backend/app/models/chat_log.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import json

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    rag_sources = Column(Text, nullable=True)           # JSON，引用文档片段
    recommended_resources = Column(Text, nullable=True) # JSON，推荐资料列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def get_rag_sources(self):
        return json.loads(self.rag_sources) if self.rag_sources else []

    def set_rag_sources(self, value):
        self.rag_sources = json.dumps(value)

    def get_recommended_resources(self):
        return json.loads(self.recommended_resources) if self.recommended_resources else []

    def set_recommended_resources(self, value):
        self.recommended_resources = json.dumps(value)