# backend/app/models/exam_record.py
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import json

class ExamRecord(Base):
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_config_id = Column(Integer, ForeignKey("exam_configs.id"), nullable=False)
    answers = Column(Text, nullable=True)               # JSON，存储每道题的答案和题目信息
    score = Column(Float, nullable=True)                # 总分
    dimensions_scores = Column(Text, nullable=True)     # JSON，各维度得分
    report_text = Column(Text, nullable=True)           # 综合评价报告
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="in_progress")  # in_progress, completed

    def get_answers(self):
        return json.loads(self.answers) if self.answers else {}

    def set_answers(self, value):
        self.answers = json.dumps(value)

    def get_dimensions_scores(self):
        return json.loads(self.dimensions_scores) if self.dimensions_scores else {}

    def set_dimensions_scores(self, value):
        self.dimensions_scores = json.dumps(value)