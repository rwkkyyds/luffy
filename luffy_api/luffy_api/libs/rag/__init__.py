"""
RAG（检索增强生成）工具包

这个包包含：
- vector_store: 纯 Python 向量存储（备选）
- faiss_store: FAISS 向量存储（默认，更快）
- rag_service: RAG 问答服务
"""

from .vector_store import SimpleVectorStore
from .faiss_store import FAISSVectorStore
from .rag_service import RAGService
