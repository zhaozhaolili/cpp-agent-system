from pydantic import BaseModel, Field
from typing import Optional, List

class TeacherInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None

class TeacherSelect(BaseModel):
    teacher_id: int

class MaterialItem(BaseModel):
    id: int
    file_name: str
    file_type: str
    chapter_id: Optional[int] = None
    chapter_title: Optional[str] = None
    uploaded_at: str

    class Config:
        from_attributes = True

class ExamListItem(BaseModel):
    config_id: int
    chapter_id: int
    chapter_title: str
    total_questions: int
    status: str  # pending, in_progress, completed
    record_id: Optional[int] = None
    score: Optional[float] = None
