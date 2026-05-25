"""
离线测试向量搜索（不需要网络）

这个脚本用模拟数据演示：
1. 如何存储课程向量
2. 如何根据问题搜索相似课程

运行方式：
    cd luffy_api
    python scripts/test_search_offline.py
"""

import os
import sys
import random

# 设置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "luffy_api"))

from libs.rag import SimpleVectorStore


def generate_mock_vector(seed: int, dim: int = 1024) -> list:
    """
    生成模拟向量
    同一个 seed 会生成相同的向量，用于模拟"相似内容有相似向量"
    """
    random.seed(seed)
    return [random.uniform(-1, 1) for _ in range(dim)]


def main():
    print("=" * 60)
    print("离线测试：向量搜索演示")
    print("=" * 60)
    
    # ========== 第一步：创建存储并添加模拟课程 ==========
    store = SimpleVectorStore()
    
    # 模拟课程数据
    # 注意：seed 相近的课程，向量也会相近（模拟语义相似）
    courses = [
        {"name": "Python入门21天", "brief": "从零开始学Python编程", "seed": 100},
        {"name": "Python进阶实战", "brief": "Python高级特性与项目实战", "seed": 105},
        {"name": "Java企业级开发", "brief": "Spring Boot微服务架构", "seed": 200},
        {"name": "前端Vue3实战", "brief": "Vue3+TypeScript现代前端开发", "seed": 300},
        {"name": "MySQL数据库优化", "brief": "数据库性能调优与架构设计", "seed": 400},
        {"name": "Linux运维实战", "brief": "服务器部署与自动化运维", "seed": 500},
        {"name": "AI大模型应用开发", "brief": "基于ChatGPT/GLM的AI应用", "seed": 600},
    ]
    
    print("\n添加模拟课程数据...")
    for i, course in enumerate(courses, 1):
        vector = generate_mock_vector(course["seed"])
        text = f"{course['name']}：{course['brief']}"
        store.add(
            text=text,
            vector=vector,
            metadata={"course_id": i, "course_name": course["name"]}
        )
        print(f"  {i}. {course['name']}")
    
    print(f"\n共添加 {len(store)} 门课程")
    
    # ========== 第二步：模拟搜索 ==========
    print("\n" + "=" * 60)
    print("开始搜索测试")
    print("=" * 60)
    
    # 测试问题列表
    test_queries = [
        ("Python怎么入门？", 102),      # seed 接近 100，应该匹配 Python 课程
        ("Java开发学什么？", 202),      # seed 接近 200，应该匹配 Java 课程
        ("前端用什么框架？", 302),      # seed 接近 300，应该匹配 Vue 课程
        ("数据库怎么优化？", 402),      # seed 接近 400，应该匹配 MySQL 课程
    ]
    
    for query, seed in test_queries:
        print(f"\n问题: {query}")
        print("-" * 40)
        
        # 生成问题的模拟向量
        query_vector = generate_mock_vector(seed)
        
        # 搜索
        results = store.search(query_vector, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata']['course_name']}")
            print(f"     相似度: {result['score']:.4f}")
    
    # ========== 第三步：演示保存和加载 ==========
    print("\n" + "=" * 60)
    print("保存和加载测试")
    print("=" * 60)
    
    # 确保 data 目录存在
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # 保存
    save_path = os.path.join(data_dir, "mock_course_vectors.json")
    store.save(save_path)
    
    # 加载到新存储
    new_store = SimpleVectorStore()
    new_store.load(save_path)
    
    # 验证加载成功
    print(f"加载后文档数: {len(new_store)}")
    
    print("\n" + "=" * 60)
    print("[OK] 测试完成！")
    print("=" * 60)
    print("\n说明：")
    print("  - 这是用模拟数据演示的")
    print("  - 真实场景中，向量来自 Embedding API")
    print("  - 相似度越高，说明课程与问题越相关")


if __name__ == "__main__":
    main()
