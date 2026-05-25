from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from utils.authentication import BlacklistJWTAuthentication
from .models import User


class UserService:
    """用户业务逻辑层"""

    @classmethod
    def check_mobile(cls, mobile):
        """检查手机号是否已注册，返回 True/False"""
        return User.objects.filter(mobile=mobile).exists()

    @classmethod
    def send_sms_code(cls, phone):
        """
        生成验证码 → 存缓存（60秒有效）→ Celery 异步发送短信
        返回生成的验证码
        """
        from libs import tencent_sms_v3
        code = tencent_sms_v3.get_code()
        cache.set('sms_cache_%s' % phone, code, 60)
        from celery_task.user_task import send_sms
        send_sms.delay(phone, code)
        return code

    @classmethod
    def register(cls, mobile, username, password):
        """
        注册用户：密码加密后通过 Celery 异步写入数据库
        密码必须在发给 Celery 之前加密，避免明文密码经过 Redis
        """
        from celery_task.user_task import create_user
        create_user.delay(
            mobile=mobile,
            username=username,
            password=make_password(password),
        )

    @classmethod
    def logout(cls, token):
        """将 token 加入 Redis 黑名单，使其失效"""
        if token:
            t = str(token)  # 统一转为字符串（simplejwt 的 AccessToken 也能 str()）
            BlacklistJWTAuthentication.revoke_token(t)
