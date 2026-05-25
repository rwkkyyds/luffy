"""
智谱 Embedding（向量化）客户端封装

这个文件的作用：
- 把文本转换成向量（一串数字）
- 向量可以用来计算"相似度"
- 是 RAG 系统的基础组件

什么是 Embedding？
- 把文字变成数字的技术
- 意思相近的文字，变成的数字也相近
- 比如 "Python" 和 "编程" 的向量很接近
"""

import requests
from typing import List


class ZhipuEmbedder:
    """
    智谱 Embedding 客户端
    
    使用方法：
        embedder = ZhipuEmbedder(api_key="你的key")
        vector = embedder.embed("Python入门教程")
        print(vector)  # [0.12, -0.34, 0.56, ...]
    """
    
    def __init__(self, api_key: str):
        """
        初始化客户端
        
        参数:
            api_key: 智谱开放平台的 API Key（和对话用同一个）
        """
        self.api_key = api_key
        # 智谱 Embedding API 的地址
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    
    def embed(self, text: str) -> List[float]:
        """
        将单个文本转换为向量
        
        参数:
            text: 要转换的文本，比如 "Python是一门编程语言"
        
        返回:
            向量列表，比如 [0.12, -0.34, 0.56, ...]
            智谱的向量是 1024 维（1024个数字）
        """
        
        # 构建请求体
        payload = {
            "model": "embedding-2",  # 智谱的向量模型，免费额度充足
            "input": text            # 要转换的文本
        }
        
        # 请求头，带上 API Key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # 发送请求
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # 解析响应
            # 智谱返回格式：
            # {
            #     "data": [
            #         {
            #             "embedding": [0.12, -0.34, ...],  # 这就是向量
            #             "index": 0
            #         }
            #     ]
            # }
            result = response.json()
            vector = result["data"][0]["embedding"]
            return vector
            
        except Exception as e:
            print(f"向量化失败: {e}")
            return []
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量将多个文本转换为向量
        
        参数:
            texts: 文本列表，比如 ["Python入门", "Java基础", "前端开发"]
        
        返回:
            向量列表的列表，每个文本对应一个向量
        
        注意：
            智谱 API 支持批量请求，但为了简单，这里用循环实现
            实际生产中可以优化为真正的批量请求
        """
        vectors = []
        for text in texts:
            vector = self.embed(text)
            vectors.append(vector)
        return vectors


# ========== 测试代码 ==========
if __name__ == "__main__":
    import os
    import sys

    API_KEY = os.environ.get("ZHIPU_API_KEY", "").strip()
    if not API_KEY:
        print("请设置环境变量 ZHIPU_API_KEY")
        sys.exit(1)

    embedder = ZhipuEmbedder(api_key=API_KEY)
    
    # 测试单个文本
    print("=" * 50)
    print("测试单个文本向量化")
    print("=" * 50)
    
    text = "Python是一门简单易学的编程语言"
    vector = embedder.embed(text)
    
    print(f"文本: {text}")
    print(f"向量维度: {len(vector)}")
    print(f"向量前5个数字: {vector[:5]}")
    
    # 测试相似度（两个相似文本的向量应该很接近）
    print("\n" + "=" * 50)
    print("测试相似度")
    print("=" * 50)
    
    text1 = "Python编程入门"
    text2 = "Python基础教程"
    text3 = "今天天气真好"
    
    v1 = embedder.embed(text1)
    v2 = embedder.embed(text2)
    v3 = embedder.embed(text3)
    
    # 计算余弦相似度（简单版本）
    def cosine_similarity(a, b):
        """计算两个向量的相似度，结果在 -1 到 1 之间，越接近 1 越相似"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        return dot_product / (norm_a * norm_b)
    
    sim_12 = cosine_similarity(v1, v2)
    sim_13 = cosine_similarity(v1, v3)
    
    print(f"'{text1}' 和 '{text2}' 的相似度: {sim_12:.4f}")
    print(f"'{text1}' 和 '{text3}' 的相似度: {sim_13:.4f}")
    print("\n结论: 相似的文本，向量相似度更高！")
