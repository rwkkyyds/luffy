"""
FAISS 向量存储

替代 SimpleVectorStore 的纯 Python 实现，使用 Facebook 的 FAISS 库做向量检索。
对于当前 43 条数据感知不大，但数据量增长到几百/几千条后，速度优势明显。

接口与 SimpleVectorStore 完全一致，可以无缝替换。
"""

import json
import os
from typing import List, Dict, Any

import numpy as np

_faiss_mod: Any = None


def _faiss():
    """
    Delay importing faiss until RAG/search code runs.

    On some Windows setups, ``import faiss`` can block or take minutes during
    process startup (OpenBLAS / DLL init). Django loads URLconf imports early,
    so a top-level ``import faiss`` makes ``runserver`` / ``migrate`` appear stuck.
    """
    global _faiss_mod
    if _faiss_mod is None:
        import faiss as _fa

        _faiss_mod = _fa
    return _faiss_mod


class FAISSVectorStore:
    """
    FAISS 向量存储

    使用方法和 SimpleVectorStore 一样：
        store = FAISSVectorStore()
        store.add("Python入门", [0.1, 0.2, ...], {"course_id": 1})
        results = store.search([0.1, 0.2, ...], top_k=3)
    """

    def __init__(self):
        self.documents = []       # 存储文本和元数据
        self.vectors = []         # 暂存原始向量（build_index 时转成 FAISS 索引）
        self.index = None         # FAISS 索引对象
        self.dimension = None     # 向量维度（第一个 add 时确定）

    def add(self, text: str, vector: List[float], metadata: Dict = None):
        """添加文档，向量先暂存，build_index() 时统一写入 FAISS"""
        self.documents.append({
            "text": text,
            "metadata": metadata or {}
        })
        self.vectors.append(vector)

        # 第一个文档确定维度
        if self.dimension is None:
            self.dimension = len(vector)

    def build_index(self):
        """把暂存的向量构建成 FAISS 索引（调用 search 前必须先调一次）"""
        if not self.vectors:
            return

        # 转成 numpy 数组，FAISS 要求 float32
        vectors_np = np.array(self.vectors, dtype='float32')

        fx = _faiss()
        # 归一化（使内积等价于余弦相似度）
        fx.normalize_L2(vectors_np)

        # 使用 IndexFlatIP：暴力搜索 + 内积，精确但速度比纯 Python 快很多
        # 数据量 < 10 万条用这个就够了，超过可以换 IndexIVFFlat
        self.index = fx.IndexFlatIP(self.dimension)
        self.index.add(vectors_np)

        # 清空暂存
        self.vectors = []

    def search(self, query_vector: List[float], top_k: int = 3) -> List[Dict]:
        """搜索最相似的文档，返回格式与 SimpleVectorStore 一致"""
        if self.index is None or self.index.ntotal == 0:
            return []

        fx = _faiss()
        # 转成 numpy 并归一化
        query = np.array([query_vector], dtype='float32')
        fx.normalize_L2(query)

        # FAISS 搜索：返回 (scores, indices)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:  # FAISS 返回 -1 表示无效结果
                continue
            doc = self.documents[idx]
            results.append({
                "text": doc["text"],
                "score": float(score),  # 内积范围 [-1, 1]，归一化后等价于余弦相似度
                "metadata": doc["metadata"]
            })

        return results

    def save(self, filepath: str):
        """保存：FAISS 索引存 .index 文件，文档元数据存 .json 文件"""
        # 保存 FAISS 索引
        index_path = filepath.replace('.json', '.index')
        if self.index is not None:
            _faiss().write_index(self.index, index_path)

        # 保存文档元数据
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

        print(f"已保存 {len(self.documents)} 条文档到 {filepath}")
        print(f"FAISS 索引保存到 {index_path}")

    def load(self, filepath: str):
        """加载：从 .index 和 .json 文件恢复"""
        index_path = filepath.replace('.json', '.index')

        # 加载文档元数据
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # 加载 FAISS 索引
        if os.path.exists(index_path):
            self.index = _faiss().read_index(index_path)
            self.dimension = self.index.d
            print(f"已加载 {len(self.documents)} 条文档 + FAISS 索引")
        else:
            # 没有 .index 文件时，需要从旧格式（.json 里带 vector）重建
            print(f"FAISS 索引文件不存在，尝试从 JSON 重建...")
            self._rebuild_from_json(filepath)

    def _rebuild_from_json(self, filepath: str):
        """兼容旧格式：从包含 vector 字段的 JSON 重建 FAISS 索引"""
        # 旧格式的 JSON 里有 vector 字段
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            return

        if not raw or 'vector' not in raw[0]:
            # 已经是新格式（没有 vector 字段），无法重建
            print("无法重建：JSON 中没有 vector 字段")
            return

        self.documents = []
        self.vectors = []
        for item in raw:
            self.documents.append({
                "text": item["text"],
                "metadata": item.get("metadata", {})
            })
            self.vectors.append(item["vector"])

        self.dimension = len(self.vectors[0])
        self.build_index()
        print(f"从旧 JSON 重建完成：{len(self.documents)} 条文档")

    def __len__(self):
        if self.index is not None:
            return self.index.ntotal
        return len(self.vectors)
