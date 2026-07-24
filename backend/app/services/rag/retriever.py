"""
RAG 检索器 — 关键词搜索 + 磁盘持久化 + 资源推荐
"""
from typing import List, Dict, Optional, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from . import persistence

# 从磁盘加载缓存（重启不丢失）
_text_cache: List[Dict] = persistence.load_cache()


def _save():
    """写入磁盘"""
    persistence.save_cache(_text_cache)


def search(query: str, top_k: int = 5, chapter_id: Optional[int] = None) -> List[Dict]:
    """检索相关文档片段"""
    return _keyword_search(query, top_k)


def _keyword_search(query: str, top_k: int = 5) -> List[Dict]:
    """关键词匹配搜索（支持中英文）"""
    if not _text_cache:
        return []

    query_lower = query.lower()
    terms = []
    import re
    en_words = re.findall(r'[a-z0-9]+', query_lower)
    terms.extend(en_words)
    chinese = re.sub(r'[a-z0-9\s]', '', query_lower)
    if len(chinese) >= 2:
        terms.extend([chinese[i:i+2] for i in range(len(chinese)-1)])
    if chinese:
        terms.append(chinese)
    terms = list(set(terms))

    scored = []
    for item in _text_cache:
        content = item.get("content", "").lower()
        score = sum(1 for t in terms if t in content)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def build_rag_context(query: str, top_k: int = 5) -> Tuple[str, List[Dict]]:
    """构建 RAG 上下文和来源信息"""
    docs = search(query, top_k=top_k)
    context_parts = []
    sources = []

    for i, doc in enumerate(docs, 1):
        meta = doc["metadata"]
        src = {
            "filename": meta.get("filename", ""),
            "chapter_title": meta.get("chapter_title", ""),
            "file_type": meta.get("file_type", ""),
        }
        if src not in sources:
            sources.append(src)
        context_parts.append(f"[资料{i}] {doc['content']}")

    context = "\n\n---\n\n".join(context_parts) if context_parts else ""
    return context, sources


def get_resource_recommendations(query: str, top_k: int = 3) -> List[Dict]:
    """根据查询推荐学习资源"""
    docs = search(query, top_k=top_k * 2)
    seen = set()
    recommendations = []
    for doc in docs:
        meta = doc["metadata"]
        key = f"{meta.get('chapter_title', '')}|{meta.get('filename', '')}"
        if key not in seen:
            seen.add(key)
            recommendations.append({
                "chapter_title": meta.get("chapter_title", ""),
                "filename": meta.get("filename", ""),
                "file_type": meta.get("file_type", ""),
            })
        if len(recommendations) >= top_k:
            break
    return recommendations


def add_text(text: str, metadata: Dict) -> int:
    """将文本切分后存入缓存并持久化到磁盘"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""]
    )
    doc = Document(page_content=text, metadata=metadata)
    chunks = splitter.split_documents([doc])

    for chunk in chunks:
        _text_cache.append({
            "content": chunk.page_content,
            "metadata": {**metadata, "chunk_index": str(len(_text_cache))}
        })

    _save()  # 写入磁盘
    print(f"[OK] RAG indexed + persisted: {len(chunks)} chunks (total {len(_text_cache)})")
    return len(chunks)


def get_count() -> int:
    return len(_text_cache)
