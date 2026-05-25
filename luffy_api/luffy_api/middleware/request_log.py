"""
请求/响应日志中间件
============================================================

这个中间件做什么：
  记录每个 HTTP 请求和响应的关键信息，方便排查问题。

记录什么：
  - 请求：方法(GET/POST)、路径、查询参数、IP、用户
  - 响应：状态码、耗时(毫秒)
  - 慢请求(>3秒)自动升级为 WARNING 级别

为什么需要它：
  - 生产环境出 bug 时，日志是唯一的线索
  - 可以发现慢接口（耗时长的请求）
  - 可以追踪某个用户的请求链路

怎么用：
  1. 在 setting/dev.py 的 MIDDLEWARE 列表里加上这行：
     'middleware.request_log.RequestLogMiddleware',
  2. 重启 Django，日志文件里就会自动记录每个请求

日志格式示例：
  INFO  GET /api/v1/course/actual/ 200 45ms ip=127.0.0.1 user=testuser
  WARN  POST /api/v1/ai/chat/ 200 3500ms ip=127.0.0.1 user=admin (慢请求)

放在 MIDDLEWARE 列表的位置：
  建议放在最前面，这样能记录到所有请求（包括被后面中间件拦截的）。
  但要放在 CorsMiddleware 之后，否则跨域请求可能被拦截。
"""
import time
import logging

logger = logging.getLogger('django')


class RequestLogMiddleware:
    """
    Django 中间件：记录请求和响应信息

    Django 中间件的工作原理：
      每个请求进来时，按 MIDDLEWARE 列表顺序依次调用每个中间件的 __call__ 方法。
      请求处理完后，响应也会经过这些中间件（可以修改响应）。

    我们的中间件在 __call__ 里做 3 件事：
      1. 记录请求开始时间
      2. 调用 get_response() 让 Django 继续处理请求（拿到响应）
      3. 计算耗时，记录日志
    """

    def __init__(self, get_response):
        """
        中间件初始化（Django 启动时调用一次）

        Args:
            get_response: 下一个中间件或视图函数的引用
                          调用它就能让请求继续往下走
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        每个请求都会调用这个方法

        Args:
            request: Django 的 HttpRequest 对象
        Returns:
            response: Django 的 HttpResponse 对象
        """
        # ========== 第一步：记录请求开始时间 ==========
        start_time = time.time()

        # ========== 第二步：让 Django 继续处理请求 ==========
        # 这一行会调用后面的中间件和视图函数，最终拿到响应
        response = self.get_response(request)

        # ========== 第三步：计算耗时，记录日志 ==========
        duration_ms = (time.time() - start_time) * 1000  # 转成毫秒

        # 取客户端 IP（可能经过 Nginx 代理，所以取 HTTP_X_FORWARDED_FOR）
        ip = self._get_client_ip(request)

        # 取用户名（未登录显示 anonymous）
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'

        # 取查询参数（?page=1&size=10 这种）
        query_string = request.META.get('QUERY_STRING', '')
        query_suffix = f'?{query_string}' if query_string else ''

        # 构造日志消息
        log_msg = (
            f'{request.method} {request.path}{query_suffix} '
            f'{response.status_code} {duration_ms:.0f}ms '
            f'ip={ip} user={username}'
        )

        # 慢请求（>3秒）用 WARNING 级别，方便从日志里快速找到
        if duration_ms > 3000:
            logger.warning(f'{log_msg} (慢请求)')
        else:
            logger.info(log_msg)

        return response

    @staticmethod
    def _get_client_ip(request):
        """
        获取客户端真实 IP

        为什么不用 request.META['REMOTE_ADDR']？
          因为项目前面有 Nginx 代理，REMOTE_ADDR 拿到的是 Nginx 的 IP。
          Nginx 会把真实 IP 放在 X-Forwarded-For 头里传过来。
          所以优先取 HTTP_X_FORWARDED_FOR，没有的话再用 REMOTE_ADDR。
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For 可能是 "client, proxy1, proxy2" 格式
            # 取第一个就是真实客户端 IP
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
