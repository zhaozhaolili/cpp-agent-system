# backend/app/models/exam_config.py
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import json

class ExamConfig(Base):
    __tablename__ = "exam_configs"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_questions = Column(Integer, nullable=False)
    choice_count = Column(Integer, default=0)
    truefalse_count = Column(Integer, default=0)
    essay_count = Column(Integer, default=0)
    programming_count = Column(Integer, default=0)
    knowledge_points = Column(Text, nullable=True)       # JSON 数组
    evaluation_dimensions = Column(Text, nullable=True)  # JSON 数组
    time_limit_minutes = Column(Integer, default=0)       # 考试时间限制（分钟，0=不限时）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def get_knowledge_points(self):
        return json.loads(self.knowledge_points) if self.knowledge_points else []

    def set_knowledge_points(self, value):
        self.knowledge_points = json.dumps(value)

    def get_evaluation_dimensions(self):
        return json.loads(self.evaluation_dimensions) if self.evaluation_dimensions else []

    def set_evaluation_dimensions(self, value):
        self.evaluation_dimensions = json.dumps(value)