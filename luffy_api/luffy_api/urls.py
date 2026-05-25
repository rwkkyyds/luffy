from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def health_check(request):
    """健康检查端点：检查数据库和 Redis 是否可用"""
    status = {"status": "ok"}
    http_status = 200

    # 检查数据库
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["db"] = "ok"
    except Exception as e:
        status["db"] = f"error: {e}"
        status["status"] = "degraded"
        http_status = 503

    # 检查 Redis
    try:
        cache.set("health_check", "ok", 10)
        cache.get("health_check")
        status["redis"] = "ok"
    except Exception as e:
        status["redis"] = f"error: {e}"
        status["status"] = "degraded"
        http_status = 503

    return JsonResponse(status, status=http_status)


from django.conf import settings
urlpatterns = [
    path('health/', health_check),  # 健康检查：GET /health/
    path('admin/', admin.site.urls),
    # API 文档（OpenAPI 3.0）
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),           # 原始 schema JSON/YAML
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),         # ReDoc
    path('api/v1/home/', include('home.urls')),
    path('api/v1/user/', include('user.urls')),
    path('api/v1/course/', include('course.urls')),
    path('api/v1/order/', include('order.urls')),
    path('api/v1/ai/', include('ai.urls')),
    path('api/v1/cart/', include('cart.urls')),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]
