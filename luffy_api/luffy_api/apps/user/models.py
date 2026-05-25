from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)  # 唯一，长度11
    # 需要pillow包的支持 ImageField继承自FileField
    icon = models.ImageField(upload_to='icon', default='icon/default.png')

    class Meta:
        db_table = 'luffy_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
