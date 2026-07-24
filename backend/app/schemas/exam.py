from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ExamConfigCreate(BaseModel):
    chapter_id: int
    total_questions: int = Field(..., ge=1, le=20)
    choice_count: int = Field(default=0, ge=0)
    truefalse_count: int = Field(default=0, ge=0)
    essay_count: int = Field(default=0, ge=0)
    programming_count: int = Field(default=0, ge=0)
    knowledge_points: List[str] = []
    evaluation_dimensions: List[str] = ["知识掌握情况", "基础概念理解", "综合分析能力"]
    time_limit_minutes: int = Field(default=0, ge=0)  # 0 = 不限时

class ExamConfigResponse(BaseModel):
    id: int
    chapter_id: int
    teacher_id: int
    total_questions: int
    choice_count: int
    truefalse_count: int
    essay_count: int
    programming_count: int = 0
    knowledge_points: List[str] = []
    evaluation_dimensions: List[str] = []
    time_limit_minutes: int = 0
    created_at: str
    chapter_title: Optional[str] = None

    class Config:
        from_attributes = True

class QuestionItem(BaseModel):
    index: int
    type: str  # choice, judge, short_answer, programming
    question: str
    options: Optional[List[str]] = None  # for choice type

class ExamStartResponse(BaseModel):
    record_id: int
    questions: List[QuestionItem]
    time_limit_minutes: int = 0

class AnswerSubmit(BaseModel):
    question_index: int
    answer: str

class ExamSubmitAll(BaseModel):
    answers: List[str] = []

class ExamReportResponse(BaseModel):
    record_id: int
    score: float
    dimensions: Dict[str, float] = {}
    review_points: List[str] = []
    overall_comment: str = ""
    completed_at: Optional[str] = None
    status: str

class ExamListResponse(BaseModel):
    id: int
    chapter_id: int
    chapter_title: str
    total_questions: int
    status: str  # pending, in_progress, completed
    score: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class ExamHistoryItem(BaseModel):
    id: int
    chapter_title: str
    score: Optional[float] = None
    status: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True
