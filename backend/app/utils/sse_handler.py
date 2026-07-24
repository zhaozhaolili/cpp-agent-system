"""
SSE (Server-Sent Events) 格式化工具
"""
import json
from typing import Any, Dict


def format_sse_data(data: str) -> bytes:
    """格式化字符串为 SSE data 事件"""
    return f"data: {data}\n\n".encode('utf-8')


def format_sse_json(data: Dict[str, Any]) -> bytes:
    """格式化 JSON 为 SSE data 事件"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode('utf-8')


def format_sse_event(event: str, data: str) -> bytes:
    """格式化带事件类型的 SSE 消息"""
    return f"event: {event}\ndata: {data}\n\n".encode('utf-8')


def format_sse_done() -> bytes:
    """发送完成标记"""
    return format_sse_json({"done": True})


def format_sse_error(message: str) -> bytes:
    """发送错误消息"""
    return format_sse_json({"error": True, "message": message})
