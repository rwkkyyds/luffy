from rest_framework.views import exception_handler
from rest_framework.response import Response
from utils.log import logger


# ============================================================
# 错误码定义：用常量代替魔术数字（之前硬编码的 998、999）
# 4xx = 客户端的错（传参错了、没登录等）
# 5xx = 服务端的错（代码bug、第三方服务挂了等）
# 999 = 兜底，不知道啥错就用这个
# ============================================================
class ErrorCode:
    SUCCESS = 100
    # 客户端错误 4xx
    VALIDATION_ERROR = 422
    AUTHENTICATION_ERROR = 401
    PERMISSION_DENIED = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    # 服务端错误 5xx
    INTERNAL_ERROR = 500
    THIRD_PARTY_ERROR = 502
    SERVICE_UNAVAILABLE = 503
    # 未知错误
    UNKNOWN_ERROR = 999


# 自定义异常基类：所有业务异常都继承它
# 用法：raise LuffyException(msg='xxx', status=422)
# 优点：代码里直接 raise 一个有意义的异常类，异常处理器会自动转成统一的 JSON 响应
class LuffyException(Exception):
    status = ErrorCode.INTERNAL_ERROR  # 默认返回 500（服务端错误）
    msg = '服务器内部错误' 

    def __init__(self, msg=None, status=None):
        if msg is not None:
            self.msg = msg
        if status is not None:
            self.status = status
        super().__init__(self.msg)


# 以下是各种具体异常类，继承 LuffyException，自动拥有 status 和 msg
# 使用示例：raise ValidationError('手机号格式不对')
#          raise NotFoundError('课程不存在')

class ValidationError(LuffyException):     # 传参错误 → 422
    status = ErrorCode.VALIDATION_ERROR
    msg = '参数校验失败'


class AuthenticationError(LuffyException):
    status = ErrorCode.AUTHENTICATION_ERROR
    msg = '认证失败'


class PermissionDeniedError(LuffyException):
    status = ErrorCode.PERMISSION_DENIED
    msg = '权限不足'


class NotFoundError(LuffyException):
    status = ErrorCode.NOT_FOUND
    msg = '资源不存在'


class ThirdPartyError(LuffyException):
    status = ErrorCode.THIRD_PARTY_ERROR
    msg = '第三方服务异常'


class ServiceUnavailableError(LuffyException):
    status = ErrorCode.SERVICE_UNAVAILABLE
    msg = '服务暂不可用'


# 全局异常处理函数（在 settings.py 的 REST_FRAMEWORK 中注册）
# 任何接口抛异常都会走这里，把异常转成统一格式的 JSON 响应
# 响应格式：{'status': 错误码, 'msg': '错误信息'}
def common_exception_handler(exc, context):
    request = context.get('request')
    view = context.get('view')

    # 第一步：让 DRF 先处理它认识的异常（比如参数校验失败、权限不足等）
    res = exception_handler(exc, context)
    if res:
        # DRF 处理了 → 把 HTTP 状态码映射成我们的 ErrorCode
        if isinstance(res.data, dict):
            detail = res.data.get('detail', str(exc))
        elif isinstance(res.data, list):
            detail = str(res.data[0]) if res.data else str(exc)
        else:
            detail = str(res.data)
        status_code = ErrorCode.VALIDATION_ERROR  # 默认按参数错误处理
        if res.status_code == 401:
            status_code = ErrorCode.AUTHENTICATION_ERROR  # 未登录 → 401
        elif res.status_code == 403:
            status_code = ErrorCode.PERMISSION_DENIED      # 没权限 → 403
        elif res.status_code == 404:
            status_code = ErrorCode.NOT_FOUND              # 资源不存在 → 404
        res = Response(data={'status': status_code, 'msg': str(detail)})
    elif isinstance(exc, LuffyException):
        # 第二步：是我们自己定义的异常类 → 直接用它的 status 和 msg
        res = Response(data={'status': exc.status, 'msg': exc.msg})
    else:
        # 第三步：其他未知异常 → 返回 999 兜底
        res = Response(data={'status': ErrorCode.UNKNOWN_ERROR, 'msg': str(exc)})

    # 不管什么异常，都记一条错误日志，方便排查问题
    try:
        logger.error('错误原因：%s, 错误视图类：%s, 请求地址：%s, 请求方式：%s' %
                     (str(exc), str(view), request.path, request.method))
    except Exception:
        logger.error('错误原因：%s' % str(exc))
    return res
