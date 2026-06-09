"""ChromaDB 向量存储服务封装"""
import chromadb
from chromadb.config import Settings
from django.conf import settings


class VectorStoreService:
    """ChromaDB 持久化客户端封装"""

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            cls._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
            )
        return cls._client

    @classmethod
    def get_collection(cls, kb_id: int):
        """获取或创建知识库对应的 collection"""
        client = cls._get_client()
        return client.get_or_create_collection(
            name=f"kb_{kb_id}",
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def add_chunks(cls, kb_id: int, ids: list[str], documents: list[str],
                   embeddings: list[list[float]], metadatas: list[dict]):
        """批量添加文档块向量"""
        collection = cls.get_collection(kb_id)
        # ChromaDB 单次最多添加 5461 条，分批处理
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
            )

    @classmethod
    def search(cls, kb_id: int, query_embedding: list[float], top_k: int = 5):
        """相似检索，返回 Top-K 结果"""
        collection = cls.get_collection(kb_id)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        if not results or not results["ids"] or not results["ids"][0]:
            return []
        items = []
        for idx in range(len(results["ids"][0])):
            items.append({
                "vector_id": results["ids"][0][idx],
                "content": results["documents"][0][idx],
                "metadata": results["metadatas"][0][idx],
                "distance": results["distances"][0][idx],
            })
        return items

    @classmethod
    def delete_by_document(cls, kb_id: int, doc_id: int):
        """按文档 ID 删除所有向量"""
        try:
            collection = cls.get_collection(kb_id)
            collection.delete(where={"doc_id": doc_id})
        except Exception:
            pass  # collection 可能不存在

    @classmethod
    def delete_collection(cls, kb_id: int):
        """删除整个知识库的 collection"""
        try:
            client = cls._get_client()
            client.delete_collection(f"kb_{kb_id}")
        except Exception:
            pass
