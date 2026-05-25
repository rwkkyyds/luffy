

from django.db import models
# 5个公共字段
class BaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')
    is_show = models.BooleanField(default=True, verbose_name='是否上架')
    orders = models.IntegerField(verbose_name='优先级')
    class Meta:
        abstract = True  # 表示它是虚拟的，不在数据库中生成表，它只用来做继承