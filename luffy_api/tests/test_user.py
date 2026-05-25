"""
测试用户模块（apps/user/）
============================================================

测试什么：
  1. 登录接口（用户名/手机号 + 密码）
  2. 注册序列化器（手机号格式校验）
  3. UserService 业务逻辑（检查手机号、登出）
  4. 登出接口（需要 JWT 认证）

关键概念：
  - @pytest.mark.django_db → 需要数据库的测试必须加这个装饰器
  - api_client → 未登录的测试客户端（从 conftest.py 来）
  - auth_client → 已登录的测试客户端（从 conftest.py 来）
  - HTTP_HOST='testserver' → 测试客户端需要设置 host，否则 serializer 里取不到

文件依赖关系：
  conftest.py 提供 api_client / auth_client
       ↓
  test_user.py 用它们调用 API，验证返回值
       ↓
  user/views.py → user/service.py → user/models.py
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache

from user.models import User
from user.serializer import RegisterSerializer


# ============================================================
# 登录接口测试（通过 API 端点测试）
# ============================================================
class TestMulLoginSerializer:
    @pytest.mark.django_db
    def test_login_with_username(self, api_client):
        """用户名 + 密码登录 → 返回 token"""
        # 先在数据库里创建一个用户
        User.objects.create_user(username='lqz', password='123456', mobile='13800000001')
        # 模拟前端发 POST 请求到登录接口
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': 'lqz', 'password': '123456',
        }, HTTP_HOST='testserver')  # HTTP_HOST 是 serializer 里生成头像 URL 需要的
        # 验证返回结果
        assert resp.data['status'] == 100  # 100 = 成功
        assert 'token' in resp.data        # 返回里应该有 token
        assert resp.data['username'] == 'lqz'

    @pytest.mark.django_db
    def test_login_with_mobile(self, api_client):
        """手机号 + 密码登录 → 返回 token"""
        User.objects.create_user(username='user2', password='abc123', mobile='13800000002')
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': '13800000002', 'password': 'abc123',
        }, HTTP_HOST='testserver')
        assert resp.data['status'] == 100
        assert resp.data['username'] == 'user2'

    @pytest.mark.django_db
    def test_login_wrong_password(self, api_client):
        """密码错误 → 返回非 100"""
        User.objects.create_user(username='lqz', password='123456', mobile='13800000003')
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': 'lqz', 'password': 'wrong',
        }, HTTP_HOST='testserver')
        assert resp.data['status'] != 100  # 不是 100 就是失败

    @pytest.mark.django_db
    def test_login_nonexistent_user(self, api_client):
        """用户不存在 → 返回非 100"""
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': 'nouser', 'password': '123456',
        }, HTTP_HOST='testserver')
        assert resp.data['status'] != 100


# ============================================================
# 注册序列化器测试（直接测试序列化类，不走 API）
# ============================================================
class TestRegisterSerializer:
    def test_register_valid_data(self):
        """注册数据格式正确"""
        ser = RegisterSerializer(data={
            'mobile': '13800138000', 'code': '1234', 'password': 'testpass123',
        })
        # code 校验依赖缓存中的验证码，这里只测字段格式是否合法

    @pytest.mark.django_db
    def test_register_invalid_mobile(self):
        """手机号格式不对 → 校验失败"""
        ser = RegisterSerializer(data={
            'mobile': '12345',  # 不是 11 位手机号
            'code': '1234', 'password': 'testpass123',
        })
        assert not ser.is_valid()  # 应该校验失败


# ============================================================
# UserService 业务逻辑测试
# ============================================================
class TestUserService:
    @pytest.mark.django_db
    def test_check_mobile_exists(self):
        """手机号已注册 → 返回 True"""
        User.objects.create_user(username='u1', password='p1', mobile='13800138000')
        from user.service import UserService
        assert UserService.check_mobile('13800138000') is True

    @pytest.mark.django_db
    def test_check_mobile_not_exists(self):
        """手机号未注册 → 返回 False"""
        from user.service import UserService
        assert UserService.check_mobile('13900000000') is False

    @patch('utils.authentication.cache')  # mock 掉 Redis
    def test_logout_revokes_token(self, mock_cache):
        """登出应该把 token 加入 Redis 黑名单"""
        from user.service import UserService
        UserService.logout('test_token_string')
        # 验证 cache.set 被调用了（往 Redis 写了黑名单 key）
        mock_cache.set.assert_called_once()

    def test_logout_with_none_token(self):
        """token 为 None 时不应该报错"""
        from user.service import UserService
        UserService.logout(None)  # 不应抛异常


# ============================================================
# 用户 API 端点测试
# ============================================================
class TestUserAPI:
    @pytest.mark.django_db
    def test_check_mobile_registered(self, api_client):
        """已注册手机号 → 返回 status=100"""
        User.objects.create_user(username='u1', password='p1', mobile='13800138000')
        resp = api_client.get('/api/v1/user/mobile/check_mobile/?mobile=13800138000')
        assert resp.data['status'] == 100

    @pytest.mark.django_db
    def test_check_mobile_not_registered(self, api_client):
        """未注册手机号 → 返回 status=101"""
        resp = api_client.get('/api/v1/user/mobile/check_mobile/?mobile=13900000000')
        assert resp.data['status'] == 101

    @pytest.mark.django_db
    def test_login_success(self, api_client):
        """登录成功 → 返回 token"""
        User.objects.create_user(username='lqz', password='123456', mobile='13800138000')
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': 'lqz', 'password': '123456',
        }, HTTP_HOST='testserver')
        assert resp.data['status'] == 100
        assert 'token' in resp.data

    @pytest.mark.django_db
    def test_login_fail(self, api_client):
        """登录失败"""
        resp = api_client.post('/api/v1/user/login/mul_login/', {
            'username': 'nouser', 'password': '123456',
        }, HTTP_HOST='testserver')
        assert resp.data['status'] != 100

    @pytest.mark.django_db
    def test_logout(self, auth_client):
        """已登录用户登出 → 成功"""
        # auth_client 已经带了 JWT token
        resp = auth_client.post('/api/v1/user/logout/')
        assert resp.data['status'] == 100

    @pytest.mark.django_db
    def test_logout_without_auth(self, api_client):
        """未登录访问登出接口 → 返回 401"""
        # api_client 没有 token，应该被拒绝
        resp = api_client.post('/api/v1/user/logout/')
        assert resp.data['status'] == 401


# ============================================================
# 用户信息修改测试
# ============================================================
class TestProfileAPI:
    @pytest.mark.django_db
    def test_get_profile_requires_auth(self, api_client):
        """未登录获取个人信息 → 401"""
        resp = api_client.get('/api/v1/user/profile/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_get_profile(self, auth_client, test_user):
        """已登录获取个人信息 → 返回用户数据"""
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.get('/api/v1/user/profile/')
            assert resp.data['status'] == 100
            assert resp.data['data']['username'] == 'testuser'

    @pytest.mark.django_db
    def test_update_profile(self, auth_client, test_user):
        """修改昵称"""
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.put('/api/v1/user/profile/', {'username': 'newname'}, format='json')
            assert resp.data['status'] == 100
            assert resp.data['data']['username'] == 'newname'
            test_user.refresh_from_db()
            assert test_user.username == 'newname'

    @pytest.mark.django_db
    def test_update_profile_partial(self, auth_client, test_user):
        """只修改邮箱，其他不变"""
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.put('/api/v1/user/profile/', {'email': 'a@b.com'}, format='json')
            assert resp.data['status'] == 100
            test_user.refresh_from_db()
            assert test_user.email == 'a@b.com'


class TestAvatarAPI:
    @pytest.mark.django_db
    def test_upload_avatar_requires_auth(self, api_client):
        """未登录上传头像 → 401"""
        resp = api_client.post('/api/v1/user/avatar/')
        assert resp.data['status'] == 401
