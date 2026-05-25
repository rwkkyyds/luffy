"""
简单的频率限制器，基于 Django 缓存（Redis）实现

核心思路：
- 每个用户/ip 对应一个 Redis key
- 访问一次，计数器 +1
- 超过上限就拒绝
- 过了时间窗口，key 自动过期，计数器归零
"""

from django.core.cache import cache


def _get_client_key(request) -> str:
    """获取当前请求的标识 key：已登录用 user_id，未登录用 IP(未登录 → 优先取代理转发的真实 IP，无代理取直连 IP)"""
    if request.user and request.user.is_authenticated:
        return f"user:{request.user.id}"
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    '''
    直接访问服务器时，该头为空；
    有代理时，值格式一般为 客户端IP, 代理1IP, 
    代理2IP,...，
    第一个 IP 是真实用户 IP。
    '''
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return f"ip:{ip}"


class RateLimiter:
    """
    频率限制器

    用法：
        limiter = RateLimiter(max_requests=20, period=60)
        allowed, remaining = limiter.check(request)
        if not allowed:
            return APIResponse(status=429, msg=f'请求太频繁，请{remaining}秒后再试')
    """

    def __init__(self, max_requests: int = 20, period: int = 60):
        self.max_requests = max_requests
        self.period = period          # 时间窗口（秒）

    def check(self, request) -> tuple:
        """
        返回 (allowed: bool, remaining_seconds: int)
        """
        key = _get_client_key(request)
        cache_key = f"ai_rl:{key}"

        try:
            # key 存在，计数+1（Redis INCR 是原子操作，无竞态问题）
            count = cache.incr(cache_key)
        except ValueError:
            # key 不存在，初始化为 1，设置过期时间
            cache.set(cache_key, 1, timeout=self.period)
            count = 1

        if count <= self.max_requests:
            return True, self.max_requests - count

        # 超限了，获取剩余过期时间
        ttl = cache.ttl(cache_key)
        return False, max(ttl, 1)


# 预设两个限流器实例
# 闲聊接口：相对便宜，限制宽松
chat_limiter = RateLimiter(max_requests=30, period=60)
# 课程问答接口：走 RAG 更贵，限制严格
course_limiter = RateLimiter(max_requests=15, period=60)
