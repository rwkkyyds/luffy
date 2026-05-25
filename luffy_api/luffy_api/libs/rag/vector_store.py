"""
简单向量存储（纯 Python 实现）

这个文件的作用：
- 存储文档和对应的向量
- 根据问题向量，找到最相似的文档
- 是 RAG 系统的核心组件

为什么用纯 Python？
- 数据量小（几十到几百条），纯 Python 完全够用
- 代码简单，容易理解原理
- 不需要额外安装依赖
- 以后数据量大了，可以轻松换成 FAISS
"""

import json
import os
from typing import List, Dict, Tuple


class SimpleVectorStore:
    """
    简单向量存储
    
    使用方法：
        store = SimpleVectorStore()
        
        # 添加文档
        store.add("Python是编程语言", [0.1, 0.2, ...], {"course_id": 1})
        
        # 搜索相似文档
        results = store.search([0.1, 0.2, ...], top_k=3)
    """
    
    def __init__(self):
        """初始化空的向量存储"""
        # 存储所有文档，每个文档是一个字典：
        # {"text": "文本内容", "vector": [向量], "metadata": {元数据}}
        self.documents = []
    
    def add(self, text: str, vector: List[float], metadata: Dict = None):
        """
        添加一个文档到存储
        
        参数:
            text: 文档的文本内容（用于展示）
            vector: 文档的向量（用于搜索）
            metadata: 额外信息，比如 {"course_id": 1, "course_name": "Python入门"}
        """
        self.documents.append({
            "text": text,
            "vector": vector,
            "metadata": metadata or {}
        })
    
    def search(self, query_vector: List[float], top_k: int = 3) -> List[Dict]:
        """
        搜索最相似的文档
        
        参数:
            query_vector: 问题的向量
            top_k: 返回最相似的几个结果
        
        返回:
            列表，每个元素包含：
            - text: 文档文本
            - score: 相似度分数（0-1，越大越相似）
            - metadata: 元数据
        """
        if not self.documents:
            return []
        
        # 计算每个文档与问题的相似度
        results = []
        for doc in self.documents:
            score = self._cosine_similarity(query_vector, doc["vector"])
            results.append({
                "text": doc["text"],
                "score": score,
                "metadata": doc["metadata"]
            })
        
        # 按相似度从高到低排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # 返回 top_k 个结果
        return results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        公式：cos(θ) = (A·B) / (|A| × |B|)
        
        返回值在 -1 到 1 之间，越接近 1 越相似
        """
        # 点积：对应位置相乘再求和
        dot_product = sum(x * y for x, y in zip(a, b))
        
        # 向量的模（长度）：各元素平方和的平方根
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        
        # 防止除以零
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def save(self, filepath: str):
        """
        保存向量存储到文件
        
        参数:
            filepath: 保存路径，如 "course_vectors.json"
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(self.documents)} 条文档到 {filepath}")
    
    def load(self, filepath: str):
        """
        从文件加载向量存储
        
        参数:
            filepath: 文件路径
        """
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}")
            return
        
        with open(filepath, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        print(f"已加载 {len(self.documents)} 条文档")
    
    def __len__(self):
        """返回文档数量"""
        return len(self.documents)


# ========== 测试代码 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("测试向量存储")
    print("=" * 50)
    
    # 创建存储
    store = SimpleVectorStore()
    
    # 模拟一些文档和向量（实际中向量来自 Embedding API）
    # 这里用简化的 3 维向量演示
    store.add(
        text="Python 是一门简单易学的编程语言，适合初学者",
        vector=[0.8, 0.6, 0.1],
        metadata={"course_id": 1, "course_name": "Python入门"}
    )
    store.add(
        text="Java 是企业级开发的首选语言",
        vector=[0.7, 0.5, 0.2],
        metadata={"course_id": 2, "course_name": "Java基础"}
    )
    store.add(
        text="前端开发需要学习 HTML、CSS、JavaScript",
        vector=[0.3, 0.2, 0.9],
        metadata={"course_id": 3, "course_name": "前端开发"}
    )
    
    print(f"\n已添加 {len(store)} 个文档")
    
    # 模拟用户提问的向量
    # 假设用户问"怎么学编程"，它的向量和 Python/Java 更接近
    query_vector = [0.75, 0.55, 0.15]
    
    print("\n搜索：'怎么学编程'（模拟向量）")
    print("-" * 30)
    
    results = store.search(query_vector, top_k=2)
    for i, result in enumerate(results, 1):  ## 注意：enumerate 从 1 开始计数
        print(f"\n第 {i} 名 (相似度: {result['score']:.4f})")
        print(f"  课程: {result['metadata']['course_name']}")
        print(f"  内容: {result['text'][:30]}...")
    
    # 测试保存和加载
    print("\n" + "=" * 50)
    print("测试保存和加载")
    print("=" * 50)
    
    store.save("test_vectors.json")
    
    new_store = SimpleVectorStore()
    new_store.load("test_vectors.json")
    print(f"\n新存储中的文档数量: {len(new_store)}")
    # 清理测试文件
    # os.remove("test_vectors.json")
    # print("测试完成，已清理临时文件")
