"""
测试购物车模块（apps/cart/）
============================================================

测试什么：
  1. CartService —— Redis 操作（add/list/remove/clear/checkout/merge）
  2. CartView API —— 接口的认证保护 + 正常流程

数据关系：
  owner = user_id(int) 或 cookie_id(str)
    └── Cart (Redis Hash: cart:{user_id} 或 cart:anonymous:{cookie_id})
          └── course_id → {price, added_at}

为什么用 mock？
  购物车数据存在 Redis 里，不走数据库。
  测试时用 mock 替掉 cache，避免依赖真实的 Redis 服务。
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from course.models import Course, Teacher
from cart.service import CartService


# ============================================================
# fixtures：准备测试数据
# ============================================================

@pytest.fixture
def cart_course(db):
    """创建一个测试课程"""
    teacher = Teacher.objects.create(name='T', role=0, title='讲师', brief='b', orders=1)
    return Course.objects.create(
        name='购物车测试课程', price=Decimal('99.00'), teacher=teacher, orders=1,
    )


@pytest.fixture
def mock_cache():
    """
    mock Redis cache，避免依赖真实 Redis
    每次测试前重置内部存储，保证测试之间互不影响。
    """
    storage = {}
    mock = MagicMock()
    mock.hset.side_effect = lambda key, field, value: storage.setdefault(key, {}).__setitem__(field, value)
    mock.hget.side_effect = lambda key, field: storage.get(key, {}).get(field)
    mock.hgetall.side_effect = lambda key: dict(storage.get(key, {}))
    mock.hdel.side_effect = lambda key, field: storage.get(key, {}).pop(field, None)
    mock.hexists.side_effect = lambda key, field: field in storage.get(key, {})
    mock.hlen.side_effect = lambda key: len(storage.get(key, {}))
    mock.expire.side_effect = lambda key, ttl: None
    mock.delete.side_effect = lambda key: storage.pop(key, None)
    with patch('cart.service._get_redis', return_value=mock):
        yield mock, storage


# ============================================================
# 测试 CartService（Redis 操作层）
# owner 统一参数：int=user_id, str=cookie_id
# ============================================================

class TestCartServiceAdd:
    @pytest.mark.django_db
    def test_add_success(self, cart_course, mock_cache):
        """添加课程 → 返回数量 1"""
        count = CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        assert count == 1

    @pytest.mark.django_db
    def test_add_duplicate(self, cart_course, mock_cache):
        """重复添加 → 抛异常"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)

    @pytest.mark.django_db
    def test_add_nonexistent_course(self, mock_cache):
        """课程不存在 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            CartService.add(owner=1, course_id=99999, price=Decimal('99.00'))

    @pytest.mark.django_db
    def test_add_with_cookie_owner(self, cart_course, mock_cache):
        """未登录（cookie）添加 → 存到 anonymous key"""
        count = CartService.add(owner='abc123', course_id=cart_course.id, price=cart_course.price)
        assert count == 1

    @pytest.mark.django_db
    def test_add_multiple_courses(self, db, mock_cache):
        """添加多门 → 数量递增"""
        teacher = Teacher.objects.create(name='T2', role=0, title='讲师', brief='b', orders=1)
        c1 = Course.objects.create(name='C1', price=Decimal('10.00'), teacher=teacher, orders=1)
        c2 = Course.objects.create(name='C2', price=Decimal('20.00'), teacher=teacher, orders=2)
        assert CartService.add(owner=1, course_id=c1.id, price=c1.price) == 1
        assert CartService.add(owner=1, course_id=c2.id, price=c2.price) == 2


class TestCartServiceList:
    @pytest.mark.django_db
    def test_list_empty(self, mock_cache):
        """空购物车 → 空列表"""
        assert CartService.list(owner=1) == []

    @pytest.mark.django_db
    def test_list_with_items(self, cart_course, mock_cache):
        """有课程 → 返回详情"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        result = CartService.list(owner=1)
        assert len(result) == 1
        assert result[0]['course_id'] == cart_course.id
        assert result[0]['name'] == '购物车测试课程'

    @pytest.mark.django_db
    def test_list_skips_deleted_course(self, cart_course, mock_cache):
        """课程被软删除 → 自动跳过"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        cart_course.is_delete = True
        cart_course.save()
        assert len(CartService.list(owner=1)) == 0

    @pytest.mark.django_db
    def test_list_with_cookie_owner(self, cart_course, mock_cache):
        """未登录查看 → 返回临时购物车"""
        CartService.add(owner='abc123', course_id=cart_course.id, price=cart_course.price)
        result = CartService.list(owner='abc123')
        assert len(result) == 1


class TestCartServiceRemove:
    @pytest.mark.django_db
    def test_remove_success(self, cart_course, mock_cache):
        """移除 → 剩余 0"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        assert CartService.remove(owner=1, course_id=cart_course.id) == 0

    @pytest.mark.django_db
    def test_remove_not_in_cart(self, cart_course, mock_cache):
        """移除不存在的课程 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            CartService.remove(owner=1, course_id=cart_course.id)

    @pytest.mark.django_db
    def test_remove_with_cookie_owner(self, cart_course, mock_cache):
        """未登录移除 → 正常工作"""
        CartService.add(owner='abc123', course_id=cart_course.id, price=cart_course.price)
        assert CartService.remove(owner='abc123', course_id=cart_course.id) == 0


class TestCartServiceClear:
    @pytest.mark.django_db
    def test_clear(self, cart_course, mock_cache):
        """清空后列表为空"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        CartService.clear(owner=1)
        assert CartService.list(owner=1) == []

    @pytest.mark.django_db
    def test_clear_with_cookie_owner(self, cart_course, mock_cache):
        """未登录清空 → 正常工作"""
        CartService.add(owner='abc123', course_id=cart_course.id, price=cart_course.price)
        CartService.clear(owner='abc123')
        assert CartService.list(owner='abc123') == []


class TestCartServiceCheckout:
    @pytest.mark.django_db
    def test_checkout_empty_cart(self, mock_cache):
        """空车结算 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            CartService.checkout(owner=1)

    @pytest.mark.django_db
    def test_checkout_returns_data(self, cart_course, mock_cache):
        """有课程 → 返回总价和列表"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        result = CartService.checkout(owner=1)
        assert result['total_amount'] == 99.0
        assert cart_course.id in result['course_ids']


class TestCartServiceMerge:
    @pytest.mark.django_db
    def test_merge_basic(self, cart_course, mock_cache):
        """临时车有课程 + 正式车为空 → 合并后正式车有该课程，临时车清空"""
        CartService.add(owner='cookie1', course_id=cart_course.id, price=cart_course.price)
        CartService.merge_cart('cookie1', user_id=1)
        assert len(CartService.list(owner=1)) == 1
        assert len(CartService.list(owner='cookie1')) == 0

    @pytest.mark.django_db
    def test_merge_no_duplicate(self, cart_course, mock_cache):
        """两边都有同一课程 → 合并后不重复"""
        CartService.add(owner=1, course_id=cart_course.id, price=cart_course.price)
        CartService.add(owner='cookie1', course_id=cart_course.id, price=cart_course.price)
        CartService.merge_cart('cookie1', user_id=1)
        assert len(CartService.list(owner=1)) == 1

    @pytest.mark.django_db
    def test_merge_preserves_user_cart(self, db, mock_cache):
        """正式车有 c1，临时车有 c2 → 合并后都有"""
        teacher = Teacher.objects.create(name='T3', role=0, title='讲师', brief='b', orders=1)
        c1 = Course.objects.create(name='C1', price=Decimal('10.00'), teacher=teacher, orders=1)
        c2 = Course.objects.create(name='C2', price=Decimal('20.00'), teacher=teacher, orders=2)
        CartService.add(owner=1, course_id=c1.id, price=c1.price)
        CartService.add(owner='cookie1', course_id=c2.id, price=c2.price)
        CartService.merge_cart('cookie1', user_id=1)
        ids = {item['course_id'] for item in CartService.list(owner=1)}
        assert ids == {c1.id, c2.id}

    @pytest.mark.django_db
    def test_merge_empty_temp_cart(self, mock_cache):
        """临时车为空 → 合并不影响正式车"""
        CartService.merge_cart('empty_cookie', user_id=1)
        assert CartService.list(owner=1) == []


# ============================================================
# 测试 CartView API（接口层）
# ============================================================

class TestCartAPIAuth:
    @pytest.mark.django_db
    def test_checkout_requires_auth(self, api_client):
        """未登录结算 → 401"""
        resp = api_client.post('/api/v1/cart/checkout/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_add_no_auth_uses_cookie(self, api_client, cart_course):
        """未登录添加 → 成功 + 设置 cookie"""
        with patch('cart.views.CartService') as mock_service:
            mock_service.add.return_value = 1
            resp = api_client.post('/api/v1/cart/add/', {
                'course_id': cart_course.id, 'price': str(cart_course.price),
            })
            assert resp.data['status'] == 100
            assert 'luffy_cart_id' in resp.cookies

    @pytest.mark.django_db
    def test_list_no_auth_empty(self, api_client):
        """未登录无 cookie 查看 → 空列表"""
        resp = api_client.get('/api/v1/cart/list/')
        assert resp.data['cart_items'] == []
        assert resp.data['cart_count'] == 0

    @pytest.mark.django_db
    def test_remove_no_auth_no_cookie(self, api_client):
        """未登录无 cookie 移除 → 401"""
        resp = api_client.delete('/api/v1/cart/remove/1/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_clear_no_auth_no_cookie(self, api_client):
        """未登录无 cookie 清空 → 401"""
        resp = api_client.delete('/api/v1/cart/clear/')
        assert resp.data['status'] == 401


class TestCartAPIAdd:
    @pytest.mark.django_db
    def test_add_success(self, auth_client, cart_course):
        """已登录添加 → 成功"""
        with patch('cart.views.CartService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_service.add.return_value = 1
            resp = auth_client.post('/api/v1/cart/add/', {
                'course_id': cart_course.id, 'price': str(cart_course.price),
            })
            assert resp.data['status'] == 100

    @pytest.mark.django_db
    def test_add_missing_course_id(self, auth_client):
        """缺少 course_id → 校验失败"""
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.post('/api/v1/cart/add/', {'price': '99.00'})
            assert resp.status_code == 200

    @pytest.mark.django_db
    def test_add_invalid_price(self, auth_client, cart_course):
        """价格不匹配 → 校验失败"""
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.post('/api/v1/cart/add/', {
                'course_id': cart_course.id, 'price': '1.00',
            })
            assert resp.status_code == 200


class TestCartAPIList:
    @pytest.mark.django_db
    def test_list_empty(self, auth_client):
        """空购物车 → 空列表"""
        with patch('cart.views.CartService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_service.list.return_value = []
            resp = auth_client.get('/api/v1/cart/list/')
            assert resp.data['status'] == 100
            assert resp.data['cart_count'] == 0

    @pytest.mark.django_db
    def test_list_with_items(self, auth_client):
        """有课程 → 返回列表"""
        with patch('cart.views.CartService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_service.list.return_value = [
                {'course_id': 1, 'name': 'Python', 'price': '99.00', 'added_at': '2026-01-01'}
            ]
            resp = auth_client.get('/api/v1/cart/list/')
            assert resp.data['status'] == 100
            assert resp.data['cart_count'] == 1


class TestCartAPIClear:
    @pytest.mark.django_db
    def test_clear_success(self, auth_client):
        """已登录清空 → 成功"""
        with patch('cart.views.CartService') as mock_service, \
             patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            mock_service.clear.return_value = None
            resp = auth_client.delete('/api/v1/cart/clear/')
            assert resp.data['status'] == 100
