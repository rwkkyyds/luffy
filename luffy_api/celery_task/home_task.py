from .celery import app
import json

from django.conf import settings
from django.core.cache import cache
from rest_framework.renderers import JSONRenderer

from home import models, serializer


@app.task
def banner_update():
    print('轮播图更新了')
    return '更新好了'


@app.task
def update_banner_list():
    """与 BannerService 一致：orders 升序；图片用相对 /media/... 即可，前端 dev 代理或浏览器可正常加载。"""
    count = getattr(settings, 'BANNER_COUNT', 10)
    queryset = models.Banner.objects.filter(
        is_delete=False, is_show=True
    ).order_by('orders')[:count]
    ser = serializer.BannerSerializer(queryset, many=True)

    banner_list = json.loads(JSONRenderer().render(ser.data).decode('utf-8'))
    cache.set('banner_list', banner_list, 86400)
    return True