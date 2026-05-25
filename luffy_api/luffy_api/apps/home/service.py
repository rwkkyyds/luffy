import json

from django.conf import settings
from django.core.cache import cache
from rest_framework.renderers import JSONRenderer

from .models import Banner
from .serializer import BannerSerializer


class BannerService:
    """
    Banner 业务逻辑层
    职责：缓存读写、数据库查询
    View 层只负责接收请求和返回响应，不关心缓存细节
    """

    CACHE_KEY = 'banner_list'
    CACHE_TTL = 24 * 60 * 60  # 24 小时

    @staticmethod
    def _serializer_data_as_plain_python(serializer):
        """把 DRF serializer.data（ReturnList）转成可 JSON / Redis 稳妥的 list[dict]，避免缓存反序列化异常。"""
        return json.loads(JSONRenderer().render(serializer.data).decode('utf-8'))

    @classmethod
    def get_banner_list(cls):
        """获取 Banner 列表，优先走缓存，缓存没有再查数据库"""
        if cache.has_key(cls.CACHE_KEY):
            return cache.get(cls.CACHE_KEY)

        # 缓存没有，查数据库
        count = getattr(settings, 'BANNER_COUNT', 10)
        queryset = Banner.objects.filter(is_delete=False, is_show=True).order_by(
            'orders'
        )[:count]
        serializer = BannerSerializer(queryset, many=True)
        banner_list = cls._serializer_data_as_plain_python(serializer)

        cache.set(cls.CACHE_KEY, banner_list, cls.CACHE_TTL)
        return banner_list

    @classmethod
    def invalidate_cache(cls):
        """清除 Banner 缓存（修改/删除/新增 Banner 后调用）"""
        cache.delete(cls.CACHE_KEY)
