"""
Chroma 向量数据库操作封装（使用本地 Embedding）
"""
import os
from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from .embedding import get_embeddings
from app.core.config import settings


class VectorStore:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        self._store: Optional[Chroma] = None
        self._ready = False

    def _load(self):
        """加载已有的向量数据库"""
        if os.path.exists(self.persist_dir) and os.path.isdir(self.persist_dir):
            try:
                files = os.listdir(self.persist_dir)
                if files and any(not f.startswith('.') for f in files):
                    self._store = Chroma(
                        persist_directory=self.persist_dir,
                        embedding_function=self.embeddings
                    )
                    cnt = self._store._collection.count()
                    print(f"[OK] Chroma loaded: {cnt} chunks")
                    return
            except Exception as e:
                print(f"[WARN] Chroma load failed: {e}")

        # 创建空的向量库
        self._store = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )
        print("[OK] Chroma created (empty)")

    def add_documents(self, documents: List[Document]) -> int:
        """添加文档到向量库"""
        try:
            self._store.add_documents(documents)
            return len(documents)
        except Exception as e:
            print(f"[WARN] Chroma write failed: {e}")
            return 0

    def search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """相似度检索"""
        if self._store is None:
            return []
        try:
            results = self._store.similarity_search(
                query, k=top_k,
                filter=filter_dict if filter_dict else None
            )
            return [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in results
            ]
        except Exception as e:
            print(f"[WARN] Search failed: {e}")
            return []

    def count(self) -> int:
        if self._store is None:
            return 0
        try:
            return self._store._collection.count()
        except Exception:
            return 0


# 全局单例
vector_store = VectorStore()
