"""
JWT 认证类——基于 djangorestframework-simplejwt，增加自定义 Redis 黑名单检查。

用法：在需要 JWT + 黑名单的 View 中设置
    authentication_classes = [BlacklistJWTAuthentication]
"""

import hashlib
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class BlacklistJWTAuthentication(JWTAuthentication):
    """
    继承 simplejwt 的 JWTAuthentication，
    增加 Redis 黑名单检查：已登出的 token 即使未过期也拒绝。

    黑名单 Key: "jwt_blacklist:{token_hash}"
    过期时间: 7 天，到期自动清理
    """

    BLACKLIST_PREFIX = "jwt_blacklist"
    BLACKLIST_TTL = 7 * 24 * 3600

    # simplejwt 用这个元组来校验 Authorization header 的前缀
    # 默认只有 'Bearer'，加上 'jwt' 兼容旧前端
    www_authenticate_realm = 'api'

    @classmethod
    def _token_key(cls, token_str: str) -> str:
        if isinstance(token_str, bytes):
            token_str = token_str.decode('utf-8')
        digest = hashlib.sha256(token_str.encode()).hexdigest()[:32]
        return f"{cls.BLACKLIST_PREFIX}:{digest}"

    def get_raw_token(self, header):
        """
        从 Authorization header 提取原始 token。
        simplejwt 默认只认 'Bearer' 前缀，这里加上 'jwt' 前缀兼容。

        Args:
            header: Authorization header 的原始字节值
        Returns:
            原始 token 字符串，或 None
        """
        if isinstance(header, bytes):
            header = header.decode('utf-8')
        parts = header.split()
        if len(parts) != 2:
            return None
        if parts[0].lower() not in ('jwt', 'bearer'):
            return None
        return parts[1]

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        if cache.get(self._token_key(str(token))):
            raise AuthenticationFailed("Token 已失效（已登出）")

        return user, token

    @classmethod
    def revoke_token(cls, token_str: str):
        """将 token 加入黑名单，TTL 7 天到期后自动清理"""
        cache.set(cls._token_key(token_str), 1, cls.BLACKLIST_TTL)
