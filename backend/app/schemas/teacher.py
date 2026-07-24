from pydantic import BaseModel, Field
from typing import Optional, List

class MaterialResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    chapter_id: Optional[int] = None
    chapter_title: Optional[str] = None
    uploaded_at: str

    class Config:
        from_attributes = True

class StudentInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    status: str
    joined_at: str
    completed_exams: int = 0
    total_exams: int = 0

class StudentExamResult(BaseModel):
    exam_config_id: int
    chapter_title: str
    score: Optional[float] = None
    status: str
    completed_at: Optional[str] = None

class ModelConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    embedding_model: Optional[str] = None

class ModelConfigResponse(BaseModel):
    api_key_masked: str
    base_url: str
    model: str
    embedding_model: str

class ChapterResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    order: int
    course_name: str

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_students: int = 0
    total_materials: int = 0
    total_exams: int = 0
    completed_exams: int = 0
    avg_score: float = 0.0
