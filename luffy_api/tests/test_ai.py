"""
测试 AI 模块（apps/ai/）
============================================================

测试什么：
  1. extract_sources —— 从 RAG 检索结果中提取课程来源信息
  2. AI 接口认证保护（需要 JWT token）
  3. 空消息和 API key 未配置的错误处理

为什么不直接 import AIService？
  AIService → from libs.rag import RAGService → import faiss / numpy
  这些依赖在测试环境可能没装，或者不重要。
  所以 extract_sources 的逻辑我们复制了一份到测试文件里单独测试，
  而 AI 接口的测试通过 API 端点 + mock 来验证。

mock 的用法：
  @patch('ai.views.AIService')  → 把 AIService 替换成假对象
  mock_ai.get_api_key.return_value = None  → 让 get_api_key 返回 None
  这样就能测试"API key 未配置"这个分支，而不需要真的调 Zhipu API
"""
import pytest
from unittest.mock import patch


# ============================================================
# extract_sources 逻辑测试
# ============================================================
# 这个函数从 RAG 检索结果中提取来源信息（课程名、章节、评分等）
# 我们复制了它的逻辑到这里，避免 import 整个 RAG 依赖链
def _extract_sources(results):
    """
    从 RAG 结果中提取来源信息
    原始代码在 ai/service.py 的 AIService.extract_sources()
    """
    sources = []
    for r in results:
        meta = r.get("metadata", {})
        sources.append({
            "course_id": meta.get("course_id"),
            "course_name": meta.get("course_name"),
            "chapter_name": meta.get("chapter_name", ""),    # 缺失时默认空字符串
            "section_name": meta.get("section_name", ""),
            "score": round(r.get("score", 0), 2),            # 保留 2 位小数
        })
    return sources


class TestExtractSources:
    def test_extract_basic(self):
        """正常提取：2 条结果 → 2 个来源"""
        results = [
            {'metadata': {'course_id': 1, 'course_name': 'Python基础', 'chapter_name': '第一章', 'section_name': '1.1'}, 'score': 0.856},
            {'metadata': {'course_id': 2, 'course_name': 'Django'}, 'score': 0.723},
        ]
        sources = _extract_sources(results)
        assert len(sources) == 2
        assert sources[0]['score'] == 0.86    # 0.856 → 四舍五入 → 0.86
        assert sources[1]['chapter_name'] == ''  # 没有 chapter_name 时默认空字符串

    def test_extract_empty(self):
        """空结果 → 空列表"""
        assert _extract_sources([]) == []


# ============================================================
# AI API 端点测试
# ============================================================
class TestAIAPI:
    @pytest.mark.django_db
    def test_chat_requires_auth(self, api_client):
        """AI 聊天接口需要认证 → 未登录返回 401"""
        resp = api_client.post('/api/v1/ai/chat/', {'message': 'hello'})
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_course_requires_auth(self, api_client):
        """课程问答接口需要认证 → 未登录返回 401"""
        resp = api_client.post('/api/v1/ai/course/', {'message': 'hello'})
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_chat_empty_message(self, auth_client):
        """空消息 → 返回 101 提示输入问题"""
        # mock AIService，让它返回一个假的 API key
        with patch('ai.views.AIService') as mock_ai:
            mock_ai.get_api_key.return_value = 'key'
            resp = auth_client.post('/api/v1/ai/chat/', {'message': ''})
            assert resp.data['status'] == 101

    @pytest.mark.django_db
    def test_chat_service_unavailable(self, auth_client):
        """API key 未配置 → 返回 503 服务不可用"""
        # mock AIService，让 get_api_key 返回 None（模拟未配置）
        with patch('ai.views.AIService') as mock_ai:
            mock_ai.get_api_key.return_value = None
            resp = auth_client.post('/api/v1/ai/chat/', {'message': 'hello'})
            assert resp.data['status'] == 503
