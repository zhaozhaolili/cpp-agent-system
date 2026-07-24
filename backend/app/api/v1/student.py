"""
学生端 API 路由
"""
import math
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from ...core.database import get_db
from ...core.config import settings
from ...api.v1.deps import get_current_student
from ...models.user import User
from ...models.chapter import Chapter
from ...models.course_material import CourseMaterial
from ...models.exam_config import ExamConfig
from ...models.exam_record import ExamRecord
from ...models.teacher_student import TeacherStudent
from ...models.wrong_answer import WrongAnswer
from ...services.cpp_runner import run_cpp_code
from ...schemas.student import (
    MaterialItem, ExamListItem, TeacherInfo, TeacherSelect
)
from ...schemas.exam import (
    ExamStartResponse, QuestionItem, AnswerSubmit,
    ExamReportResponse, ExamHistoryItem
)
from ...services.exam_service import exam_service

router = APIRouter(prefix="/student", tags=["学生端"])


# ── 资料浏览 ─────────────────────────────────────

@router.get("/materials")
def list_materials(
    chapter_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """浏览可用的课程资料（分页）"""
    # 获取学生的教师
    rel = db.query(TeacherStudent).filter(
        TeacherStudent.student_id == current_user.id,
        TeacherStudent.status == "active"
    ).first()

    if not rel:
        # 没有教师，返回所有资料
        q = db.query(CourseMaterial)
    else:
        q = db.query(CourseMaterial).filter(
            CourseMaterial.teacher_id == rel.teacher_id
        )

    if chapter_id is not None:
        q = q.filter(CourseMaterial.chapter_id == chapter_id)

    total = q.count()
    materials = q.order_by(CourseMaterial.uploaded_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()

    result = []
    for m in materials:
        chapter_title = None
        if m.chapter_id:
            ch = db.query(Chapter).filter(Chapter.id == m.chapter_id).first()
            if ch:
                chapter_title = ch.title
        result.append(MaterialItem(
            id=m.id,
            file_name=m.file_name,
            file_type=m.file_type,
            chapter_id=m.chapter_id,
            chapter_title=chapter_title,
            uploaded_at=m.uploaded_at.isoformat() if m.uploaded_at else "",
        ))
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/materials/{material_id}/download")
def download_material(
    material_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """下载/查看资料文件"""
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(404, "资料不存在")

    file_path = os.path.join(settings.UPLOAD_DIR, material.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(404, "文件不存在")

    return FileResponse(file_path, filename=material.file_name)


# ── 考核功能 ─────────────────────────────────────

@router.get("/exams")
def list_exams(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """查看可用的考核列表（含完成状态，分页）"""
    # 获取学生的教师，找到教师配置的考核
    rel = db.query(TeacherStudent).filter(
        TeacherStudent.student_id == current_user.id,
        TeacherStudent.status == "active"
    ).first()

    if not rel:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    q = db.query(ExamConfig).filter(
        ExamConfig.teacher_id == rel.teacher_id
    ).order_by(ExamConfig.created_at)

    total = q.count()
    configs = q.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for cfg in configs:
        chapter = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
        chapter_title = chapter.title if chapter else "未知章节"

        # 检查该学生是否已完成此考核
        record = db.query(ExamRecord).filter(
            ExamRecord.student_id == current_user.id,
            ExamRecord.exam_config_id == cfg.id
        ).order_by(ExamRecord.started_at.desc()).first()

        status = "pending"
        record_id = None
        score = None
        if record:
            status = record.status
            record_id = record.id
            score = record.score

        result.append(ExamListItem(
            config_id=cfg.id,
            chapter_id=cfg.chapter_id,
            chapter_title=chapter_title,
            total_questions=cfg.total_questions,
            status=status,
            record_id=record_id,
            score=score,
        ))
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.post("/exams/{config_id}/start", response_model=ExamStartResponse)
async def start_exam(
    config_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """开始考核（调用 LLM 生成题目）"""
    cfg = db.query(ExamConfig).filter(ExamConfig.id == config_id).first()
    if not cfg:
        raise HTTPException(404, "考核配置不存在")

    chapter = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
    if not chapter:
        raise HTTPException(404, "章节不存在")

    # 检查是否已有进行中的考核
    existing = db.query(ExamRecord).filter(
        ExamRecord.student_id == current_user.id,
        ExamRecord.exam_config_id == config_id,
        ExamRecord.status == "in_progress"
    ).first()
    if existing:
        questions_data = existing.get_answers()
        question_list = questions_data.get("questions", [])
        # Ensure each question has an index field (补全 index)
        for i, q in enumerate(question_list):
            if "index" not in q:
                q["index"] = i
        return ExamStartResponse(
            record_id=existing.id,
            questions=[QuestionItem(**q) for q in question_list]
        )

    # 调用 LLM 生成题目
    question_config = {
        "choice": cfg.choice_count,
        "judge": cfg.truefalse_count,
        "short_answer": cfg.essay_count,
        "programming": cfg.programming_count or 0,
    }
    questions = await exam_service.generate_questions(
        chapter_title=chapter.title,
        knowledge_points=cfg.get_knowledge_points(),
        config=question_config,
    )

    if not questions:
        raise HTTPException(500, "题目生成失败，请稍后重试")

    # 创建考试记录
    # 给每道题加 index 字段（LLM 返回的题目没有 index）
    for i, q in enumerate(questions):
        q["index"] = i

    # 不含答案的题目列表（用于返回给前端）
    questions_without_answers = []
    for q in questions:
        questions_without_answers.append({
            "index": q["index"],
            "type": q.get("type", ""),
            "question": q.get("question", ""),
            "options": q.get("options"),
        })

    record = ExamRecord(
        student_id=current_user.id,
        exam_config_id=config_id,
        status="in_progress",
    )
    record.set_answers({"questions": questions, "student_answers": {}})
    db.add(record)
    db.commit()
    db.refresh(record)

    return ExamStartResponse(
        record_id=record.id,
        questions=[QuestionItem(**q) for q in questions_without_answers],
        time_limit_minutes=cfg.time_limit_minutes or 0,
    )


@router.post("/exams/{record_id}/answer")
def submit_answer(
    record_id: int,
    answer: AnswerSubmit,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """提交单题答案"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.student_id == current_user.id,
        ExamRecord.status == "in_progress"
    ).first()
    if not record:
        raise HTTPException(404, "考核记录不存在或已结束")

    data = record.get_answers()
    student_answers = data.get("student_answers", {})
    student_answers[str(answer.question_index)] = answer.answer
    data["student_answers"] = student_answers
    record.set_answers(data)
    db.commit()

    return {"message": "答案已保存", "answered": len(student_answers)}


@router.post("/exams/{record_id}/submit", response_model=ExamReportResponse)
async def submit_all(
    record_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """提交全部答案并触发批改"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.student_id == current_user.id,
        ExamRecord.status == "in_progress"
    ).first()
    if not record:
        raise HTTPException(404, "考核记录不存在或已结束")

    data = record.get_answers()
    questions = data.get("questions", [])
    student_answers_dict = data.get("student_answers", {})

    # 构建答案列表（按题号排序）
    answers_list = []
    for i in range(len(questions)):
        answers_list.append(student_answers_dict.get(str(i), "(未作答)"))

    # 调用 LLM 批改
    report = await exam_service.grade_exam(questions, answers_list)

    # 获取章节标题
    cfg = db.query(ExamConfig).filter(ExamConfig.id == record.exam_config_id).first()
    chapter_title = ""
    if cfg:
        ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
        chapter_title = ch.title if ch else ""

    # 提取错题并保存
    wrong_answers = exam_service.extract_wrong_answers(questions, answers_list)
    for wa in wrong_answers:
        db.add(WrongAnswer(
            student_id=current_user.id,
            exam_record_id=record.id,
            chapter_title=chapter_title,
            question_type=wa["question_type"],
            question_text=wa["question_text"],
            correct_answer=wa["correct_answer"],
            student_answer=wa["student_answer"],
        ))

    # 更新记录
    record.score = report.get("score", 0)
    record.set_dimensions_scores(report.get("dimensions", {}))
    record.report_text = report.get("overall_comment", "")
    record.status = "completed"
    record.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(record)

    return ExamReportResponse(
        record_id=record.id,
        score=record.score or 0,
        dimensions=record.get_dimensions_scores(),
        review_points=report.get("review_points", []),
        overall_comment=report.get("overall_comment", ""),
        completed_at=record.completed_at.isoformat() if record.completed_at else None,
        status=record.status,
    )


@router.get("/exams/{record_id}/report", response_model=ExamReportResponse)
def get_report(
    record_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """查看学习评价报告"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.student_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(404, "考核记录不存在")

    return ExamReportResponse(
        record_id=record.id,
        score=record.score or 0,
        dimensions=record.get_dimensions_scores(),
        review_points=[],
        overall_comment=record.report_text or "",
        completed_at=record.completed_at.isoformat() if record.completed_at else None,
        status=record.status,
    )


@router.get("/exams/history")
def exam_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """考核历史记录（分页）"""
    q = db.query(ExamRecord).filter(
        ExamRecord.student_id == current_user.id
    ).order_by(ExamRecord.started_at.desc())

    total = q.count()
    records = q.offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for r in records:
        cfg = db.query(ExamConfig).filter(ExamConfig.id == r.exam_config_id).first()
        chapter_title = ""
        if cfg:
            ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
            chapter_title = ch.title if ch else ""

        result.append(ExamHistoryItem(
            id=r.id,
            chapter_title=chapter_title,
            score=r.score,
            status=r.status,
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
        ))
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ── 错题本 ─────────────────────────────────────

@router.get("/wrong-answers")
def get_wrong_answers(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """查看我的错题本（分页）"""
    q = db.query(WrongAnswer).filter(
        WrongAnswer.student_id == current_user.id
    ).order_by(WrongAnswer.created_at.desc())

    total = q.count()
    wrongs = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": w.id,
                "chapter_title": w.chapter_title,
                "question_type": w.question_type,
                "question_text": w.question_text,
                "correct_answer": w.correct_answer,
                "student_answer": w.student_answer,
                "created_at": w.created_at.isoformat() if w.created_at else "",
            }
            for w in wrongs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.delete("/wrong-answers/{wrong_id}")
def delete_wrong_answer(
    wrong_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """删除单条错题（已掌握）"""
    wa = db.query(WrongAnswer).filter(
        WrongAnswer.id == wrong_id,
        WrongAnswer.student_id == current_user.id,
    ).first()
    if not wa:
        raise HTTPException(404, "错题不存在")
    db.delete(wa)
    db.commit()
    return {"message": "已删除"}


# ── 导出报告 ───────────────────────────────

@router.get("/exams/{record_id}/export")
def export_report(
    record_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """导出考核报告为 HTML（浏览器打印 → PDF）"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.student_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(404, "考核记录不存在")

    cfg = db.query(ExamConfig).filter(ExamConfig.id == record.exam_config_id).first()
    ch_title = ""
    if cfg:
        ch = db.query(Chapter).filter(Chapter.id == cfg.chapter_id).first()
        ch_title = ch.title if ch else ""

    dims = record.get_dimensions_scores()
    dim_html = ""
    for k, v in dims.items():
        color = "#67C23A" if float(v) >= 80 else ("#E6A23C" if float(v) >= 60 else "#F56C6C")
        dim_html += f"""
        <div style="margin:8px 0;">
            <span>{k}</span>
            <div style="background:#eee;border-radius:4px;height:20px;width:100%;margin-top:4px;">
                <div style="background:{color};height:100%;width:{v}%;border-radius:4px;"></div>
            </div>
            <span style="float:right;font-size:12px;">{v}分</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>学习评价报告</title>
<style>
    body{{font-family:'Microsoft YaHei',sans-serif;max-width:700px;margin:40px auto;padding:20px;color:#333;}}
    h1{{text-align:center;color:#409EFF;}} h2{{border-bottom:2px solid #409EFF;padding-bottom:8px;}}
    .score{{text-align:center;font-size:64px;font-weight:bold;color:#409EFF;margin:20px 0;}}
    .meta{{text-align:center;color:#999;margin-bottom:30px;}}
    .review{{background:#fdf6ec;padding:16px;border-radius:8px;margin:16px 0;}}
    .review li{{margin:6px 0;}} .comment{{line-height:1.8;margin:16px 0;}}
    @media print{{body{{margin:0;padding:20px;}}}}
</style></head>
<body>
    <h1>C++ 课程考核报告</h1>
    <div class="meta">
        <p>学生: {current_user.full_name or current_user.username} | 章节: {ch_title}</p>
        <p>完成时间: {record.completed_at.isoformat() if record.completed_at else '-'}</p>
    </div>
    <div class="score">{int(record.score or 0)}<span style="font-size:20px;"> / 100</span></div>
    <h2>评价维度</h2>
    {dim_html}
    <h2>综合评价</h2>
    <div class="comment">{record.report_text or '暂无'}</div>
    <div style="text-align:center;margin-top:40px;color:#999;font-size:12px;">
        C++ 课程智能体系统 自动生成
    </div>
</body></html>"""

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


# ── C++ 在线运行 ───────────────────────────────

from pydantic import BaseModel

class CppRunRequest(BaseModel):
    code: str
    stdin: str = ""

@router.post("/cpp-run")
def run_cpp(req: CppRunRequest, current_user=Depends(get_current_student)):
    """编译并运行 C++ 代码"""
    result = run_cpp_code(req.code, req.stdin)
    return result


# ── 教师选择 ─────────────────────────────────────

@router.get("/teachers", response_model=List[TeacherInfo])
def list_teachers(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """查看可选教师列表"""
    teachers = db.query(User).filter(User.role == "teacher").all()
    return [
        TeacherInfo(id=t.id, username=t.username, full_name=t.full_name)
        for t in teachers
    ]


@router.get("/teacher", response_model=Optional[TeacherInfo])
def get_my_teacher(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """查看我当前的教师"""
    rel = db.query(TeacherStudent).filter(
        TeacherStudent.student_id == current_user.id,
        TeacherStudent.status == "active"
    ).first()
    if not rel:
        return None

    teacher = db.query(User).filter(User.id == rel.teacher_id).first()
    if not teacher:
        return None
    return TeacherInfo(id=teacher.id, username=teacher.username, full_name=teacher.full_name)


@router.post("/teacher", response_model=TeacherInfo)
def select_teacher(
    selection: TeacherSelect,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """选择/更换教师"""
    teacher = db.query(User).filter(
        User.id == selection.teacher_id,
        User.role == "teacher"
    ).first()
    if not teacher:
        raise HTTPException(404, "教师不存在")

    # 取消原有关系
    db.query(TeacherStudent).filter(
        TeacherStudent.student_id == current_user.id,
        TeacherStudent.status == "active"
    ).update({"status": "inactive"})

    # 创建新关系
    rel = TeacherStudent(
        teacher_id=selection.teacher_id,
        student_id=current_user.id,
        status="active"
    )
    db.add(rel)
    db.commit()

    return TeacherInfo(id=teacher.id, username=teacher.username, full_name=teacher.full_name)
