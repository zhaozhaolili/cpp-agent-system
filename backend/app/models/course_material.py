# backend/app/models/course_material.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)  # 可为空，若未指定章节
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)       # pdf, pptx, docx, md等
    parsed_content = Column(Text, nullable=True)         # 可选，存储解析后的纯文本，方便检索
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())