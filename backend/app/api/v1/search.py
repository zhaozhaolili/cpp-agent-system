"""
全局搜索 API
"""
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.api.v1.deps import get_current_active_user
from app.models.user import User
from app.models.chat_log import ChatLog
from app.models.course_material import CourseMaterial
from app.models.wrong_answer import WrongAnswer
from app.models.teacher_student import TeacherStudent

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("")
def global_search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    scope: str = Query("all", description="搜索范围: all/chat/materials/students/wrong_answers"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """全局搜索 - 根据 scope 在不同范围内检索"""
    keyword = f"%{q}%"
    results = []
    total = 0

    if scope in ("all", "chat"):
        # 搜索对话记录
        chat_q = db.query(ChatLog).filter(
            ChatLog.user_id == current_user.id,
            or_(
                ChatLog.question.like(keyword),
                ChatLog.answer.like(keyword),
            )
        )
        if scope == "chat":
            total = chat_q.count()
            logs = chat_q.order_by(ChatLog.created_at.desc()).offset(
                (page - 1) * page_size).limit(page_size).all()
            results = [
                {
                    "id": log.id,
                    "question": log.question[:100],
                    "answer": (log.answer or "")[:100],
                    "created_at": log.created_at.isoformat(),
                    "type": "chat",
                }
                for log in logs
            ]

    if scope in ("all", "materials"):
        # 搜索资料
        if current_user.role == "teacher":
            material_q = db.query(CourseMaterial).filter(
                CourseMaterial.teacher_id == current_user.id,
                or_(
                    CourseMaterial.file_name.like(keyword),
                    CourseMaterial.parsed_content.like(keyword),
                )
            )
        else:
            # 学生可以看到其教师的资料
            rel = db.query(TeacherStudent).filter(
                TeacherStudent.student_id == current_user.id,
                TeacherStudent.status == "active"
            ).first()
            if rel:
                material_q = db.query(CourseMaterial).filter(
                    CourseMaterial.teacher_id == rel.teacher_id,
                    or_(
                        CourseMaterial.file_name.like(keyword),
                        CourseMaterial.parsed_content.like(keyword),
                    )
                )
            else:
                material_q = db.query(CourseMaterial).filter(
                    CourseMaterial.file_name.like(keyword),
                )

        if scope == "materials":
            total = material_q.count()
            materials = material_q.order_by(CourseMaterial.uploaded_at.desc()).offset(
                (page - 1) * page_size).limit(page_size).all()
            results = [
                {
                    "id": m.id,
                    "file_name": m.file_name,
                    "file_type": m.file_type,
                    "parsed_content": (m.parsed_content or "")[:100],
                    "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else "",
                    "type": "material",
                }
                for m in materials
            ]

    if scope in ("all", "students"):
        # 搜索学生（仅教师可用）
        if current_user.role == "teacher":
            # 找到教师的活跃学生
            student_subs = db.query(TeacherStudent.student_id).filter(
                TeacherStudent.teacher_id == current_user.id,
                TeacherStudent.status == "active"
            ).subquery()

            student_q = db.query(User).filter(
                User.id.in_(db.query(student_subs.c.student_id)),
                User.role == "student",
                or_(
                    User.username.like(keyword),
                    User.full_name.like(keyword),
                )
            )

            if scope == "students":
                total = student_q.count()
                students = student_q.order_by(User.created_at.desc()).offset(
                    (page - 1) * page_size).limit(page_size).all()
                results = [
                    {
                        "id": s.id,
                        "username": s.username,
                        "full_name": s.full_name,
                        "role": s.role,
                        "created_at": s.created_at.isoformat(),
                        "type": "student",
                    }
                    for s in students
                ]

    if scope in ("all", "wrong_answers"):
        # 搜索错题（仅自己的）
        wa_q = db.query(WrongAnswer).filter(
            WrongAnswer.student_id == current_user.id,
            WrongAnswer.question_text.like(keyword),
        )

        if scope == "wrong_answers":
            total = wa_q.count()
            wrongs = wa_q.order_by(WrongAnswer.created_at.desc()).offset(
                (page - 1) * page_size).limit(page_size).all()
            results = [
                {
                    "id": w.id,
                    "chapter_title": w.chapter_title,
                    "question_type": w.question_type,
                    "question_text": w.question_text[:100],
                    "correct_answer": w.correct_answer,
                    "student_answer": w.student_answer,
                    "created_at": w.created_at.isoformat() if w.created_at else "",
                    "type": "wrong_answer",
                }
                for w in wrongs
            ]

    # 对于 scope="all"，需要合并多个来源的结果并手动分页
    if scope == "all":
        all_items = []

        # chat
        chat_q = db.query(ChatLog).filter(
            ChatLog.user_id == current_user.id,
            or_(
                ChatLog.question.like(keyword),
                ChatLog.answer.like(keyword),
            )
        )
        for log in chat_q.order_by(ChatLog.created_at.desc()).limit(50).all():
            all_items.append({
                "id": log.id,
                "question": log.question[:100],
                "answer": (log.answer or "")[:100],
                "created_at": log.created_at.isoformat(),
                "type": "chat",
            })

        # materials
        if current_user.role == "teacher":
            material_q = db.query(CourseMaterial).filter(
                CourseMaterial.teacher_id == current_user.id,
                or_(
                    CourseMaterial.file_name.like(keyword),
                    CourseMaterial.parsed_content.like(keyword),
                )
            )
        else:
            rel = db.query(TeacherStudent).filter(
                TeacherStudent.student_id == current_user.id,
                TeacherStudent.status == "active"
            ).first()
            if rel:
                material_q = db.query(CourseMaterial).filter(
                    CourseMaterial.teacher_id == rel.teacher_id,
                    or_(
                        CourseMaterial.file_name.like(keyword),
                        CourseMaterial.parsed_content.like(keyword),
                    )
                )
            else:
                material_q = db.query(CourseMaterial).filter(
                    CourseMaterial.file_name.like(keyword),
                )

        for m in material_q.order_by(CourseMaterial.uploaded_at.desc()).limit(50).all():
            all_items.append({
                "id": m.id,
                "file_name": m.file_name,
                "file_type": m.file_type,
                "parsed_content": (m.parsed_content or "")[:100],
                "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else "",
                "type": "material",
            })

        # students (teacher only)
        if current_user.role == "teacher":
            student_subs = db.query(TeacherStudent.student_id).filter(
                TeacherStudent.teacher_id == current_user.id,
                TeacherStudent.status == "active"
            ).subquery()

            student_q = db.query(User).filter(
                User.id.in_(db.query(student_subs.c.student_id)),
                User.role == "student",
                or_(
                    User.username.like(keyword),
                    User.full_name.like(keyword),
                )
            )
            for s in student_q.order_by(User.created_at.desc()).limit(50).all():
                all_items.append({
                    "id": s.id,
                    "username": s.username,
                    "full_name": s.full_name,
                    "role": s.role,
                    "created_at": s.created_at.isoformat(),
                    "type": "student",
                })

        # wrong answers (own only)
        wa_q = db.query(WrongAnswer).filter(
            WrongAnswer.student_id == current_user.id,
            WrongAnswer.question_text.like(keyword),
        )
        for w in wa_q.order_by(WrongAnswer.created_at.desc()).limit(50).all():
            all_items.append({
                "id": w.id,
                "chapter_title": w.chapter_title,
                "question_type": w.question_type,
                "question_text": w.question_text[:100],
                "correct_answer": w.correct_answer,
                "student_answer": w.student_answer,
                "created_at": w.created_at.isoformat() if w.created_at else "",
                "type": "wrong_answer",
            })

        total = len(all_items)
        # 手动分页
        start = (page - 1) * page_size
        end = start + page_size
        results = all_items[start:end]

    return {
        "scope": scope,
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }
