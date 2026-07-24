"""
RAG 资料服务（兼容旧接口，委托到 services/rag/ 子模块）
"""
from typing import List, Dict

from app.services.rag.vector_store import vector_store
from app.core.config import settings


class RAGService:
    """RAG 检索服务（单例）"""

    def __init__(self):
        self.vector_store = vector_store
        self.persist_dir = settings.CHROMA_PERSIST_DIR

    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        """检索相关文档片段"""
        return self.vector_store.search(query, top_k=top_k)

    def get_chunk_count(self) -> int:
        """获取向量库中的文档片段数量"""
        return self.vector_store.count()


# 全局单例
rag_service = RAGService()
