"""
测试请求日志中间件
============================================================

测试什么：
  1. 中间件能正常处理请求（不报错、不阻塞）
  2. 响应状态码正确传递
  3. IP 获取逻辑
  4. 慢请求识别

怎么测中间件：
  中间件就是一个 Python 类，可以直接实例化测试。
  也可以通过 API 客户端发请求，验证日志输出。
"""
import pytest
from unittest.mock import patch, MagicMock
from middleware.request_log import RequestLogMiddleware


class TestRequestLogMiddleware:
    def test_middleware_passes_response(self):
        """中间件应该正常传递响应，不改变内容"""
        # 构造一个假的 get_response（模拟后面的中间件/视图）
        mock_response = MagicMock()
        mock_response.status_code = 200
        get_response = MagicMock(return_value=mock_response)

        middleware = RequestLogMiddleware(get_response)
        # 构造一个假的 request
        request = MagicMock()
        request.method = 'GET'
        request.path = '/api/test/'
        request.META = {'QUERY_STRING': '', 'REMOTE_ADDR': '127.0.0.1'}
        request.user = MagicMock(is_authenticated=False, username='anon')

        response = middleware(request)

        # 响应应该原样传递
        assert response.status_code == 200
        # get_response 应该被调用了一次
        get_response.assert_called_once_with(request)

    def test_get_client_ip_from_remote_addr(self):
        """没有 X-Forwarded-For 时，取 REMOTE_ADDR"""
        request = MagicMock()
        request.META = {'REMOTE_ADDR': '192.168.1.100'}
        ip = RequestLogMiddleware._get_client_ip(request)
        assert ip == '192.168.1.100'

    def test_get_client_ip_from_forwarded_for(self):
        """有 X-Forwarded-For 时，取第一个 IP（真实客户端）"""
        request = MagicMock()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '10.0.0.1, 192.168.1.1',
            'REMOTE_ADDR': '192.168.1.1',
        }
        ip = RequestLogMiddleware._get_client_ip(request)
        assert ip == '10.0.0.1'

    def test_get_client_ip_no_meta(self):
        """没有 IP 信息时返回 unknown"""
        request = MagicMock()
        request.META = {}
        ip = RequestLogMiddleware._get_client_ip(request)
        assert ip == 'unknown'

    @pytest.mark.django_db
    def test_middleware_in_request_chain(self, api_client):
        """中间件在实际请求链中不报错"""
        # 发一个真实请求，中间件应该正常记录日志
        resp = api_client.get('/api/v1/course/category/')
        assert resp.status_code == 200
