"""
AI 模块路由配置

URL 设计：
- POST /api/v1/ai/chat/    → 普通 AI 问答（不使用 RAG）
- POST /api/v1/ai/course/  → 课程智能问答（使用 RAG）
"""

from django.urls import path
from . import views

urlpatterns = [
    # 普通 AI 问答（不使用 RAG）
    path('chat/', views.ChatView.as_view(), name='ai-chat'),
    # 流式闲聊
    path('chat/stream/', views.ChatStreamView.as_view(), name='ai-chat-stream'),

    # 课程智能问答（使用 RAG）
    path('course/', views.CourseQAView.as_view(), name='ai-course'),
    # 流式课程问答
    path('course/stream/', views.CourseQAStreamView.as_view(), name='ai-course-stream'),
]
