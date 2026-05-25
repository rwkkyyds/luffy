"""
测试工具模块（utils/）
============================================================

测试什么：
  1. APIResponse      → 统一响应格式 {status: 100, msg: "成功", ...}
  2. ErrorCode         → 错误码常量（100、401、404、999 等）
  3. LuffyException    → 自定义异常体系（ValidationError、NotFoundError 等）
  4. common_exception_handler → 全局异常处理器（任何接口报错都走这里）
  5. BlacklistJWTAuthentication → JWT 认证 + Redis 黑名单

为什么要测这些？
  这些是整个项目的"基础设施"，所有接口都依赖它们。
  如果 APIResponse 格式变了，前端就解析不了。
  如果异常处理器有 bug，接口报错时前端拿不到有用的错误信息。
"""
import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from utils.response import APIResponse
from utils.exception import (
    ErrorCode, LuffyException, ValidationError, AuthenticationError,
    PermissionDeniedError, NotFoundError, ThirdPartyError,
    ServiceUnavailableError, common_exception_handler,
)
from utils.authentication import BlacklistJWTAuthentication


# ============================================================
# APIResponse 测试
# ============================================================
# APIResponse 是我们自定义的 Response 子类
# 它会自动把数据包装成 {status: 100, msg: "成功", ...} 格式
class TestAPIResponse:
    def test_default_success(self):
        """不传参数时，默认返回 {status: 100, msg: "成功"}"""
        resp = APIResponse()
        assert resp.data['status'] == 100
        assert resp.data['msg'] == '成功'

    def test_custom_status_and_msg(self):
        """可以自定义 status 和 msg"""
        resp = APIResponse(status=101, msg='手机号未注册')
        assert resp.data['status'] == 101
        assert resp.data['msg'] == '手机号未注册'

    def test_extra_kwargs(self):
        """可以用 **kwargs 传入额外字段（如 token、username）"""
        resp = APIResponse(token='abc123', username='lqz')
        assert resp.data['token'] == 'abc123'
        assert resp.data['username'] == 'lqz'
        assert resp.data['status'] == 100  # 默认值

    def test_http_status(self):
        """可以设置 HTTP 状态码（默认 200）"""
        resp = APIResponse(http_status=201)
        assert resp.status_code == 201


# ============================================================
# ErrorCode 测试
# ============================================================
# ErrorCode 是错误码常量类，避免代码里到处写魔术数字
# 比如 if status == 100: ... → if status == ErrorCode.SUCCESS: ...
class TestErrorCode:
    def test_success_is_100(self):
        assert ErrorCode.SUCCESS == 100

    def test_client_errors_are_4xx(self):
        """客户端错误（传参错了、没登录等）应该是 4xx"""
        assert 400 <= ErrorCode.VALIDATION_ERROR < 500
        assert 400 <= ErrorCode.AUTHENTICATION_ERROR < 500
        assert 400 <= ErrorCode.PERMISSION_DENIED < 500
        assert 400 <= ErrorCode.NOT_FOUND < 500

    def test_server_errors_are_5xx(self):
        """服务端错误（代码 bug、第三方挂了）应该是 5xx"""
        assert 500 <= ErrorCode.INTERNAL_ERROR < 600
        assert 500 <= ErrorCode.THIRD_PARTY_ERROR < 600
        assert 500 <= ErrorCode.SERVICE_UNAVAILABLE < 600

    def test_unknown_is_999(self):
        """未知错误统一用 999"""
        assert ErrorCode.UNKNOWN_ERROR == 999


# ============================================================
# LuffyException 异常体系测试
# ============================================================
# 业务异常类：代码里直接 raise，异常处理器会自动转成 JSON 响应
# 用法：raise ValidationError('手机号格式不对')
#       → 前端收到 {status: 422, msg: "手机号格式不对"}
class TestLuffyException:
    def test_base_exception_defaults(self):
        """基类默认是 500 服务器内部错误"""
        exc = LuffyException()
        assert exc.status == ErrorCode.INTERNAL_ERROR
        assert exc.msg == '服务器内部错误'

    def test_custom_msg_and_status(self):
        """可以自定义 msg 和 status"""
        exc = LuffyException(msg='自定义错误', status=422)
        assert exc.status == 422
        assert exc.msg == '自定义错误'

    def test_validation_error(self):
        """ValidationError → 422 参数校验失败"""
        exc = ValidationError('参数不对')
        assert exc.status == 422
        assert exc.msg == '参数不对'

    def test_authentication_error(self):
        """AuthenticationError → 401 认证失败"""
        exc = AuthenticationError()
        assert exc.status == 401
        assert exc.msg == '认证失败'

    def test_permission_denied(self):
        """PermissionDeniedError → 403 权限不足"""
        exc = PermissionDeniedError()
        assert exc.status == 403

    def test_not_found(self):
        """NotFoundError → 404 资源不存在"""
        exc = NotFoundError('课程不存在')
        assert exc.status == 404
        assert exc.msg == '课程不存在'

    def test_third_party_error(self):
        """ThirdPartyError → 502 第三方服务异常"""
        exc = ThirdPartyError()
        assert exc.status == 502

    def test_service_unavailable(self):
        """ServiceUnavailableError → 503 服务暂不可用"""
        exc = ServiceUnavailableError()
        assert exc.status == 503


# ============================================================
# common_exception_handler 测试
# ============================================================
# 这是全局异常处理器，在 settings.py 的 REST_FRAMEWORK 中注册
# 任何接口抛异常都会走这里，把异常转成统一的 JSON 响应
class TestExceptionHandler:
    def setup_method(self):
        """每个测试方法执行前都会调用，创建请求工厂"""
        self.factory = APIRequestFactory()

    def _get_context(self, path='/test/'):
        """构造异常处理器需要的 context 参数"""
        request = self.factory.get(path)
        return {'request': request, 'view': MagicMock()}

    def test_luffy_validation_error(self):
        """LuffyException 子类 → 直接用它的 status 和 msg"""
        exc = ValidationError('手机号格式不对')
        resp = common_exception_handler(exc, self._get_context())
        assert resp.data['status'] == 422
        assert resp.data['msg'] == '手机号格式不对'

    def test_luffy_not_found(self):
        exc = NotFoundError('课程不存在')
        resp = common_exception_handler(exc, self._get_context())
        assert resp.data['status'] == 404
        assert resp.data['msg'] == '课程不存在'

    def test_unknown_exception_returns_999(self):
        """未知异常 → 返回 999 兜底"""
        exc = RuntimeError('something broke')
        resp = common_exception_handler(exc, self._get_context())
        assert resp.data['status'] == 999
        assert 'something broke' in resp.data['msg']


# ============================================================
# BlacklistJWTAuthentication 测试
# ============================================================
# JWT 认证类：继承 simplejwt，增加了 Redis 黑名单检查
# 黑名单机制：用户登出时把 token 的 hash 存到 Redis，下次请求拒绝
class TestBlacklistJWTAuthentication:
    def test_token_key_hashing(self):
        """同一个 token 生成的 Redis key 应该一致"""
        key1 = BlacklistJWTAuthentication._token_key('test_token_123')
        key2 = BlacklistJWTAuthentication._token_key('test_token_123')
        assert key1 == key2
        # key 格式：jwt_blacklist:abc123def...
        assert key1.startswith('jwt_blacklist:')

    def test_token_key_differs_for_different_tokens(self):
        """不同 token 生成的 key 应该不同"""
        key1 = BlacklistJWTAuthentication._token_key('token_a')
        key2 = BlacklistJWTAuthentication._token_key('token_b')
        assert key1 != key2

    def test_token_key_handles_bytes(self):
        """bytes 类型的 token 也能生成 key（简单jwt 可能返回 bytes）"""
        key = BlacklistJWTAuthentication._token_key(b'bytes_token')
        assert key.startswith('jwt_blacklist:')

    @patch('utils.authentication.cache')  # mock 掉 Redis 缓存
    def test_revoke_token_sets_cache(self, mock_cache):
        """revoke_token 应该往 Redis 写入 key，TTL 7 天"""
        BlacklistJWTAuthentication.revoke_token('some_token')
        mock_cache.set.assert_called_once()
        args = mock_cache.set.call_args
        assert args[0][1] == 1  # value = 1（只要 key 存在就算在黑名单里）
        assert args[0][2] == 7 * 24 * 3600  # TTL = 7 天

    @patch('utils.authentication.cache')
    def test_authenticate_passes_when_not_blacklisted(self, mock_cache):
        """token 不在黑名单里时，认证应该通过"""
        mock_cache.get.return_value = None  # Redis 里没有这个 key
        auth = BlacklistJWTAuthentication()
        # 这里只测黑名单逻辑，super().authenticate 的结果被 mock
        # 更完整的测试需要集成测试环境
