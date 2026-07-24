"""
本地 Embedding 封装（自动选择可用方案，无需外部 API）
优先: sentence-transformers（最佳中文效果）
回退: Chroma ONNX 内置模型（轻量，无需 PyTorch）
"""
from langchain_core.embeddings import Embeddings
from typing import List
import os

MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "shibing624/text2vec-base-chinese")
_embedding_instance = None


def _create_st_embeddings():
    """方案1: sentence-transformers（中文效果好，需要 PyTorch）"""
    from sentence_transformers import SentenceTransformer

    class STEmbeddings(Embeddings):
        def __init__(self, model_name):
            print(f"[INFO] Loading sentence-transformers: {model_name}")
            self.model = SentenceTransformer(model_name)

        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return self.model.encode(texts, normalize_embeddings=True).tolist()

        def embed_query(self, text: str) -> List[float]:
            return self.model.encode([text], normalize_embeddings=True)[0].tolist()

    return STEmbeddings(MODEL_NAME)


def _create_onnx_embeddings():
    """方案2: Chroma ONNX 内置模型（轻量，无需 PyTorch，英文为主）"""
    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        ef = ONNXMiniLM_L6_V2()

        class ONNXEmbeddings(Embeddings):
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return ef(texts).tolist()

            def embed_query(self, text: str) -> List[float]:
                return ef([text])[0].tolist()

        return ONNXEmbeddings()
    except ImportError:
        return None


def get_embeddings() -> Embeddings:
    """获取最佳可用的 Embedding 实例"""
    global _embedding_instance
    if _embedding_instance is not None:
        return _embedding_instance

    # 方案1: 尝试 sentence-transformers（最佳效果）
    try:
        _embedding_instance = _create_st_embeddings()
        print("[OK] Using sentence-transformers embedding")
        return _embedding_instance
    except ImportError:
        print("[WARN] sentence-transformers not installed, trying ONNX fallback...")
    except Exception as e:
        print(f"[WARN] sentence-transformers failed: {e}")

    # 方案2: Chroma ONNX 内置模型
    onnx = _create_onnx_embeddings()
    if onnx is not None:
        _embedding_instance = onnx
        print("[OK] Using Chroma ONNX embedding (English-optimized)")
        return _embedding_instance

    raise RuntimeError(
        "No embedding model available. "
        "Install sentence-transformers: pip install sentence-transformers"
    )
