"""
系统管理 API 路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ...core.database import get_db
from ...api.v1.deps import get_current_active_user
from ...models.user import User
from ...models.chat_log import ChatLog
from ...models.exam_record import ExamRecord
from ...models.course_material import CourseMaterial

router = APIRouter(prefix="/admin", tags=["系统管理"])


@router.get("/stats")
def system_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """系统统计数据"""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_teachers = db.query(func.count(User.id)).filter(User.role == "teacher").scalar() or 0
    total_students = db.query(func.count(User.id)).filter(User.role == "student").scalar() or 0
    total_chats = db.query(func.count(ChatLog.id)).scalar() or 0
    total_exams = db.query(func.count(ExamRecord.id)).scalar() or 0
    total_materials = db.query(func.count(CourseMaterial.id)).scalar() or 0

    return {
        "total_users": total_users,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_chats": total_chats,
        "total_exams": total_exams,
        "total_materials": total_materials,
    }


@router.get("/logs")
def system_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """查看最近的系统调用日志（对话记录）"""
    logs = db.query(ChatLog).order_by(
        ChatLog.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "question": log.question[:100] + "..." if len(log.question) > 100 else log.question,
            "answer_preview": (log.answer or "")[:200] + "..." if len(log.answer or "") > 200 else (log.answer or ""),
            "sources": log.get_rag_sources(),
            "created_at": log.created_at.isoformat() if log.created_at else "",
        }
        for log in logs
    ]
