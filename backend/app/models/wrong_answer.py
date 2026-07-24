"""错题本模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class WrongAnswer(Base):
    __tablename__ = "wrong_answers"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False)
    chapter_title = Column(String(200), nullable=True)
    question_type = Column(String(20), nullable=False)  # choice/judge/short_answer/programming
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
