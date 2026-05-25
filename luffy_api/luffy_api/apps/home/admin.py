from django.contrib import admin

from .models import Banner
from .service import BannerService


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'link','is_show', 'is_delete')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        BannerService.invalidate_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        BannerService.invalidate_cache()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        BannerService.invalidate_cache()

    # 增加自定义按钮
    actions = ['make_copy']
    def make_copy(self, request, queryset):
        # 选中一些数据，点击 【自定义按钮】  触发方法执行，传入你选中 queryset
        # 保存，删除
        print(queryset)
    make_copy.short_description = '自定义按钮'