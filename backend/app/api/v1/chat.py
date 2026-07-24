"""
对话 API — SSE 流式 + RAG + 资源推荐
"""
import math
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...services.llm_service import llm_service
from ...services.rag.retriever import build_rag_context, get_resource_recommendations
from ...api.v1.deps import get_current_user
from ...core.database import get_db
from ...models.user import User
from ...models.chat_log import ChatLog

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    question: str


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """SSE 流式对话（含 RAG 检索 + 资源推荐）"""
    try:
        # 1. RAG 检索
        context, sources = build_rag_context(request.question, top_k=5)
        recommendations = get_resource_recommendations(request.question, top_k=3)

        # 2. 构建推荐文本
        rec_text = ""
        if recommendations:
            rec_parts = []
            for r in recommendations:
                ch = r.get("chapter_title", "")
                fn = r.get("filename", "")
                ft = r.get("file_type", "")
                if ch:
                    rec_parts.append(f"- {ch} → {fn} ({ft})")
                else:
                    rec_parts.append(f"- {fn} ({ft})")
            rec_text = "\n\n## 学习资源推荐\n\n" + "\n".join(rec_parts) + "\n"

        # 3. 构建 prompt
        system_prompt = f"""你是一位专业的 C++ 课程助教，教授课程为「面向对象方法与C++程序设计」。

请基于以下课程资料回答学生问题，回答要专业、准确、条理清晰。

**课程资料（来自教师上传的课件）：**
{context if context else "（知识库中暂无相关内容，请基于你的通用知识回答）"}

**回答规范：**
- 开头用 1-2 句话直接回答问题
- 使用 ## 和 ### 组织内容层级
- 代码块必须指定语言（```cpp）
- 核心概念使用 **粗体**，关键术语使用 `代码格式`
- 表格使用标准 Markdown 表格语法
- 最后给出总结（使用 ## 总结）

**请在回答末尾附上学习资源推荐部分：**
{rec_text if rec_text else "(No related resources)"}

**At the very end of your response, output a JSON array of 2-3 follow-up questions on the LAST line only (do NOT include in the main answer text):**
[FOLLOWUP]
["question1?", "question2?"]
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.question}
        ]

        full_answer = ""

        async def generate():
            nonlocal full_answer
            try:
                async for chunk in llm_service.stream_chat(messages):
                    full_answer += chunk
                    yield f"data: {chunk}\n\n".encode('utf-8')
            except Exception as e:
                err = f"生成错误: {str(e)}"
                yield f"data: {err}\n\n".encode('utf-8')
            finally:
                # 解析追问
                followups = []
                if "[FOLLOWUP]" in full_answer:
                    parts = full_answer.split("[FOLLOWUP]")
                    main_answer = parts[0].strip()
                    try:
                        import re
                        match = re.search(r'\[.*?\]', parts[1])
                        if match:
                            followups = eval(match.group())
                    except:
                        pass
                    full_answer = main_answer  # 去掉原始回答中的 FOLLOWUP 标记

                done = {
                    "done": True,
                    "sources": [s.get("filename", "") for s in sources],
                    "recommendations": recommendations,
                    "followups": followups,
                }
                yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n".encode('utf-8')

                # 保存对话日志
                try:
                    chat_log = ChatLog(
                        user_id=current_user.id,
                        question=request.question,
                        answer=full_answer,
                    )
                    chat_log.set_rag_sources([s.get("filename", "") for s in sources])
                    chat_log.set_recommended_resources(recommendations)
                    db.add(chat_log)
                    db.commit()
                except Exception as e:
                    print(f"[WARN] Chat log save failed: {e}")
                    db.rollback()

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.get("/conversations")
async def get_conversations(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取对话列表（分页，仅返回每个对话的第一条问题作为标题）"""
    q = db.query(ChatLog).filter(
        ChatLog.user_id == current_user.id
    ).order_by(ChatLog.created_at.desc())

    total = q.count()
    logs = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": log.id,
                "title": log.question[:60] + ("..." if len(log.question) > 60 else ""),
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/history")
async def get_chat_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的对话历史（分页）"""
    q = db.query(ChatLog).filter(
        ChatLog.user_id == current_user.id
    ).order_by(ChatLog.created_at.desc())

    total = q.count()
    logs = q.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": log.id,
                "question": log.question,
                "answer": log.answer[:200] + "..." if len(log.answer or "") > 200 else (log.answer or ""),
                "sources": log.get_rag_sources(),
                "recommended_resources": log.get_recommended_resources(),
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/history/{chat_id}")
async def get_chat_detail(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取单条对话完整内容"""
    log = db.query(ChatLog).filter(
        ChatLog.id == chat_id,
        ChatLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(404, "对话不存在")

    return {
        "id": log.id,
        "question": log.question,
        "answer": log.answer or "",
        "sources": log.get_rag_sources(),
        "recommended_resources": log.get_recommended_resources(),
        "created_at": log.created_at.isoformat()
    }


@router.delete("/history/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除单条对话"""
    log = db.query(ChatLog).filter(
        ChatLog.id == chat_id,
        ChatLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(404, "对话不存在")
    db.delete(log)
    db.commit()
    return {"message": "已删除"}


@router.delete("/history")
async def delete_all_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """清空当前用户所有对话历史"""
    count = db.query(ChatLog).filter(
        ChatLog.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": f"已删除 {count} 条对话"}
