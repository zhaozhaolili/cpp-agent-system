"""
RAG 知识库持久化 — 将内存缓存写入磁盘 JSON 文件，重启后恢复
"""
import json
import os
from typing import List, Dict

from app.core.config import settings

CACHE_FILE = os.path.join(settings.CHROMA_PERSIST_DIR, "rag_cache.json")


def save_cache(cache: List[Dict]) -> None:
    """将内存缓存写入磁盘"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"[OK] RAG cache saved: {len(cache)} chunks")
    except Exception as e:
        print(f"[WARN] Failed to save RAG cache: {e}")


def load_cache() -> List[Dict]:
    """从磁盘加载缓存"""
    if not os.path.exists(CACHE_FILE):
        print("[OK] RAG cache: no saved data, starting fresh")
        return []
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[OK] RAG cache loaded: {len(data)} chunks")
        return data
    except Exception as e:
        print(f"[WARN] Failed to load RAG cache: {e}")
        return []
