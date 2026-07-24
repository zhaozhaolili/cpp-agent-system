"""
学习仪表盘 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List

from ...core.database import get_db
from ...api.v1.deps import get_current_student, get_current_teacher
from ...models.user import User
from ...models.chapter import Chapter
from ...models.exam_config import ExamConfig
from ...models.exam_record import ExamRecord
from ...models.teacher_student import TeacherStudent
from ...models.wrong_answer import WrongAnswer
from ...models.course_material import CourseMaterial

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/student")
def student_dashboard(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """学生仪表盘"""
    # 全部章节数
    total_chapters = db.query(func.count(Chapter.id)).scalar() or 0

    # 已完成考核数
    completed_count = db.query(func.count(ExamRecord.id)).filter(
        ExamRecord.student_id == current_user.id,
        ExamRecord.status == "completed"
    ).scalar() or 0

    # 平均分
    avg_score = db.query(func.avg(ExamRecord.score)).filter(
        ExamRecord.student_id == current_user.id,
        ExamRecord.status == "completed"
    ).scalar() or 0

    # 各维度平均得分（从所有已完成考核汇总）
    records = db.query(ExamRecord).filter(
        ExamRecord.student_id == current_user.id,
        ExamRecord.status == "completed"
    ).all()

    dim_scores = {}
    dim_count = {}
    for r in records:
        dims = r.get_dimensions_scores()
        for k, v in dims.items():
            dim_scores[k] = dim_scores.get(k, 0) + float(v)
            dim_count[k] = dim_count.get(k, 0) + 1

    dimensions = {}
    for k in dim_scores:
        dimensions[k] = round(dim_scores[k] / dim_count[k], 1)

    # 错题数
    wrong_count = db.query(func.count(WrongAnswer.id)).filter(
        WrongAnswer.student_id == current_user.id
    ).scalar() or 0

    # 最近考核
    recent = db.query(ExamRecord).filter(
        ExamRecord.student_id == current_user.id
    ).order_by(ExamRecord.started_at.desc()).limit(5).all()

    recent_exams = []
    for r in recent:
        cfg = db.query(ExamConfig).filter(ExamConfig.id == r.exam_config_id).first()
        ch_title = ""
        if cfg:
            ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
            ch_title = ch.title if ch else ""
        recent_exams.append({
            "id": r.id,
            "chapter_title": ch_title,
            "score": r.score,
            "status": r.status,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        })

    return {
        "total_chapters": total_chapters,
        "completed_exams": completed_count,
        "progress_percent": round(completed_count / total_chapters * 100, 1) if total_chapters > 0 else 0,
        "avg_score": round(float(avg_score), 1),
        "dimensions": dimensions,
        "wrong_count": wrong_count,
        "recent_exams": recent_exams,
    }


@router.get("/teacher")
def teacher_dashboard(
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """教师仪表盘"""
    # 学生数
    student_count = db.query(func.count(TeacherStudent.id)).filter(
        TeacherStudent.teacher_id == current_user.id,
        TeacherStudent.status == "active"
    ).scalar() or 0

    # 资料数
    material_count = db.query(func.count(CourseMaterial.id)).filter(
        CourseMaterial.teacher_id == current_user.id
    ).scalar() or 0

    # 考核配置数
    exam_configs = db.query(ExamConfig).filter(
        ExamConfig.teacher_id == current_user.id
    ).all()
    config_count = len(exam_configs)

    # 所有学生的成绩分布
    scores = []
    chapter_pass = {}  # 章节 → (通过数, 总数)
    for cfg in exam_configs:
        ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
        ch_title = ch.title if ch else f"章节{cfg.chapter_id}"
        chapter_records = db.query(ExamRecord).filter(
            ExamRecord.exam_config_id == cfg.id,
            ExamRecord.status == "completed"
        ).all()
        passed = sum(1 for r in chapter_records if (r.score or 0) >= 60)
        total = len(chapter_records)
        chapter_pass[ch_title] = {
            "passed": passed,
            "total": total,
            "rate": round(passed / total * 100, 1) if total > 0 else 0,
        }
        for r in chapter_records:
            if r.score is not None:
                scores.append(r.score)

    # 分数分布
    dist = {"0-39": 0, "40-59": 0, "60-79": 0, "80-100": 0}
    for s in scores:
        if s < 40:
            dist["0-39"] += 1
        elif s < 60:
            dist["40-59"] += 1
        elif s < 80:
            dist["60-79"] += 1
        else:
            dist["80-100"] += 1

    avg_all = round(sum(scores) / len(scores), 1) if scores else 0

    # 最近提交
    recent = db.query(ExamRecord).filter(
        ExamRecord.status == "completed"
    ).join(ExamConfig, ExamRecord.exam_config_id == ExamConfig.id).filter(
        ExamConfig.teacher_id == current_user.id
    ).order_by(ExamRecord.completed_at.desc()).limit(10).all()

    recent_list = []
    for r in recent:
        student = db.query(User).filter(User.id == r.student_id).first()
        cfg = db.query(ExamConfig).filter(ExamConfig.id == r.exam_config_id).first()
        ch_title = ""
        if cfg:
            ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
            ch_title = ch.title if ch else ""
        recent_list.append({
            "student_name": student.full_name or student.username if student else "?",
            "chapter_title": ch_title,
            "score": r.score,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        })

    return {
        "student_count": student_count,
        "material_count": material_count,
        "config_count": config_count,
        "total_submissions": len(scores),
        "avg_score": avg_all,
        "score_distribution": dist,
        "chapter_pass_rate": chapter_pass,
        "recent_activity": recent_list,
    }
