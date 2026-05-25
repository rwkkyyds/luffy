from .models import Banner
from .serializer import BannerSerializer
from .service import BannerService
from utils.response import APIResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    list=extend_schema(tags=['首页'], summary='获取轮播图列表', description='返回所有可用的轮播图，带 24 小时 Redis 缓存。'),
    update=extend_schema(tags=['首页'], summary='更新轮播图'),
)
class BannerView(GenericViewSet, ListModelMixin, UpdateModelMixin):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def list(self, request, *args, **kwargs):
        # 缓存逻辑已抽到 BannerService，view 只做"调用 + 返回"
        banner_list = BannerService.get_banner_list()
        return APIResponse(result=banner_list)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        BannerService.invalidate_cache()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        BannerService.invalidate_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        BannerService.invalidate_cache()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)