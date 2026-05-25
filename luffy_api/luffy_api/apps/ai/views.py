"""
AI 问答视图

接口列表：
- POST /api/v1/ai/chat/              普通闲聊（一次性返回）
- POST /api/v1/ai/chat/stream/       普通闲聊（SSE 流式）
- POST /api/v1/ai/course/            课程问答 RAG（一次性返回）
- POST /api/v1/ai/course/stream/     课程问答 RAG（SSE 流式）
"""

import json as _json
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from utils.authentication import BlacklistJWTAuthentication
from utils.response import APIResponse
from utils.throttle import chat_limiter, course_limiter
from .service import AIService
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


def _check_limiter(limiter, request):
    """限流检查，返回 None 表示通过，返回 APIResponse 表示被限流"""
    allowed, remaining = limiter.check(request)
    if not allowed:
        return APIResponse(status=429, msg=f'请求太频繁，请{remaining}秒后再试')
    return None


def _get_message_and_history(request):
    """从请求中提取消息和历史，返回 (message, history) 或 (None, None)"""
    message = request.data.get("message", "").strip()
    if not message:
        return None, None
    history = request.data.get("history", [])
    if not isinstance(history, list):
        history = []
    return message, history


@extend_schema(tags=['AI'], summary='AI 闲聊', description='普通 AI 问答（不使用 RAG），一次性返回完整回答。需要 JWT 认证。请求体：{"message": "问题", "history": []}')
class ChatView(APIView):
    """POST /api/v1/ai/chat/ —— 普通 AI 问答，一次性返回"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resp = _check_limiter(chat_limiter, request)
        if resp:
            return resp
        if not AIService.get_api_key():
            return APIResponse(status=503, msg='AI 服务未配置')
        message, history = _get_message_and_history(request)
        if not message:
            return APIResponse(status=101, msg="请输入您的问题")
        answer = AIService.chat(message, history)
        return APIResponse(data={"answer": answer})


@extend_schema(tags=['AI'], summary='AI 闲聊（流式）', description='SSE 流式返回，打字机效果。需要 JWT 认证。')
class ChatStreamView(APIView):
    """POST /api/v1/ai/chat/stream/ —— 流式闲聊，打字机效果"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resp = _check_limiter(chat_limiter, request)
        if resp:
            return resp
        if not AIService.get_api_key():
            return APIResponse(status=503, msg='AI 服务未配置')
        message, history = _get_message_and_history(request)
        if not message:
            return APIResponse(status=101, msg="请输入您的问题")

        def event_stream():
            for chunk in AIService.chat_stream(message, history):
                yield f"data: {_json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {_json.dumps({'done': True})}\n\n"

        resp = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'
        return resp


@extend_schema(tags=['AI'], summary='课程智能问答', description='使用 RAG 检索课程知识库，返回回答和来源。需要 JWT 认证。')
class CourseQAView(APIView):
    """POST /api/v1/ai/course/ —— 课程智能问答，使用 RAG"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resp = _check_limiter(course_limiter, request)
        if resp:
            return resp
        if not AIService.get_rag_service():
            return APIResponse(status=503, msg='AI 服务未配置')
        message, history = _get_message_and_history(request)
        if not message:
            return APIResponse(status=101, msg="请输入您的问题")
        result = AIService.course_qa(message, history)
        return APIResponse(data=result)


@extend_schema(tags=['AI'], summary='课程智能问答（流式）', description='RAG + SSE 流式输出。需要 JWT 认证。')
class CourseQAStreamView(APIView):
    """POST /api/v1/ai/course/stream/ —— RAG + 流式输出"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resp = _check_limiter(course_limiter, request)
        if resp:
            return resp
        if not AIService.get_rag_service():
            return APIResponse(status=503, msg='AI 服务未配置')
        message, history = _get_message_and_history(request)
        if not message:
            return APIResponse(status=101, msg="请输入您的问题")

        stream, sources = AIService.course_qa_stream(message, history)

        def event_stream():
            for chunk in stream:
                yield f"data: {_json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {_json.dumps({'done': True, 'sources': sources}, ensure_ascii=False)}\n\n"

        resp = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'
        return resp
