"""
conftest.py —— pytest 共享 fixtures（测试"工具人"）
============================================================

这个文件的作用：
  定义所有测试文件都能直接使用的"公共工具"。
  pytest 会自动加载 conftest.py，不需要 import。

什么是 fixture？
  fixture 就是"测试前的准备工作"。
  比如：创建测试用户、创建数据库连接、准备测试数据等。
  你写 def test_xxx(api_client): 就能直接用，不用自己创建。

这个文件提供了 3 个 fixture：

  1. api_client    → 未认证的 API 测试客户端（模拟前端发请求）
  2. test_user     → 一个测试用户对象（写入测试数据库）
  3. auth_client   → 带 JWT token 的测试客户端（模拟已登录用户）

它们之间的关系：
  auth_client = api_client + test_user 的 JWT token
       ↓              ↓
  已登录请求      未登录请求

使用示例：
  def test_public_api(api_client):       # 不需要登录的接口
      resp = api_client.get('/api/v1/course/actual/')

  def test_private_api(auth_client):     # 需要登录的接口
      resp = auth_client.post('/api/v1/user/logout/')

  def test_user_data(test_user):         # 需要用户对象
      assert test_user.username == 'testuser'
"""
import pytest
from rest_framework.test import APIClient
from user.models import User


@pytest.fixture
def api_client():
    """
    未认证的 DRF 测试客户端

    这个客户端模拟前端发 HTTP 请求，但不带任何登录信息。
    用来测试不需要登录的接口（如课程列表、轮播图）。

    返回：APIClient 实例
    用法：resp = api_client.get('/api/v1/course/actual/')
    """
    return APIClient()


@pytest.fixture
def db(django_db_setup, django_db_blocker):
    """
    数据库 fixture（pytest-django 内置）

    参数里的 db 表示"需要数据库"。
    pytest-django 看到这个参数就会：
      1. 创建 SQLite 内存数据库
      2. 运行 Django migrate 创建表
      3. 测试结束后自动清理

    不需要手动调用，只要在测试函数参数里写 db 就行：
      def test_something(db):  ← 自动获得数据库
    """
    with django_db_blocker.unblock():
        yield


@pytest.fixture
def test_user(db):
    """
    创建一个测试用户，写入测试数据库

    这个用户会作为"已登录用户"使用。
    auth_client fixture 依赖它来生成 JWT token。

    返回：User 对象（已保存到数据库）
    用法：def test_xxx(test_user):
              assert test_user.username == 'testuser'
    """
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        mobile='13800138000',
    )


@pytest.fixture
def auth_client(api_client, test_user):
    """
    带 JWT token 的测试客户端（模拟已登录用户）

    工作原理：
      1. 用 test_user 生成一个 JWT access token
      2. 把 token 设置到 api_client 的请求头里
      3. 之后这个客户端发的所有请求都会带上 Authorization: jwt xxx
      4. 后端的 BlacklistJWTAuthentication 会识别这个 token

    注意：这个 fixture 依赖 api_client 和 test_user，
         pytest 会自动帮你创建它们，不用手动传。

    返回：APIClient 实例（已设置 JWT 认证头）
    用法：resp = auth_client.post('/api/v1/user/logout/')
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    # RefreshToken.for_user(user) → 为用户签发一对 token（access + refresh）
    # .access_token → 取出 access token 对象
    # str(...) → 转成 JWT 字符串（eyJhbGci... 这种格式）
    token = str(RefreshToken.for_user(test_user).access_token)
    # credentials() 设置请求头，后端就能从 Authorization 头读到 token
    api_client.credentials(HTTP_AUTHORIZATION=f'jwt {token}')
    return api_client
