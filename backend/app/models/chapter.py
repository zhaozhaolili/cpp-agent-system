# backend/app/models/chapter.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)          # 如 "第一章 面向对象概述"
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)              # 排序
    course_name = Column(String(100), default="面向对象方法与C++程序设计")
    created_at = Column(DateTime(timezone=True), server_default=func.now())