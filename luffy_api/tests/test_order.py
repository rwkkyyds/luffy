"""
测试订单模块（apps/order/）
============================================================

测试什么：
  1. OrderService.check_order_paid() —— 检查订单是否已支付
  2. 订单创建接口的认证保护
  3. 支付宝同步回调接口（前端二次验证）

数据关系：
  User (买家)
    └── Order (订单)
          └── OrderDetail (订单详情) → Course (课程)

订单状态：
  0 = 未支付（默认）
  1 = 已支付
  2 = 已取消
  3 = 超时取消
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from user.models import User
from course.models import Course, Teacher
from order.models import Order, OrderDetail
from order.service import OrderService


@pytest.fixture
def order_data(db):
    """
    创建测试订单数据

    包含：一个用户、一个教师、一个课程、一个未支付订单
    """
    user = User.objects.create_user(username='buyer', password='123', mobile='13800000001')
    teacher = Teacher.objects.create(name='T', role=0, title='讲师', brief='b', orders=1)
    course = Course.objects.create(
        name='Test Course', price=Decimal('50.00'), teacher=teacher, orders=1,
    )
    order = Order.objects.create(
        subject='购买Test Course', total_amount=Decimal('50.00'),
        out_trade_no='test_order_001', user=user, order_status=0,  # 默认未支付
    )
    OrderDetail.objects.create(order=order, course=course, price=Decimal('50.00'), real_price=Decimal('50.00'))
    return {'user': user, 'course': course, 'order': order}


class TestOrderService:
    @pytest.mark.django_db
    def test_check_order_paid_true(self, order_data):
        """已支付订单 → 返回 True"""
        order_data['order'].order_status = 1  # 改为已支付
        order_data['order'].save()
        assert OrderService.check_order_paid('test_order_001') is True

    @pytest.mark.django_db
    def test_check_order_paid_false(self, order_data):
        """未支付订单 → 返回 False"""
        assert OrderService.check_order_paid('test_order_001') is False

    @pytest.mark.django_db
    def test_check_order_not_exist(self):
        """不存在的订单 → 返回 False"""
        assert OrderService.check_order_paid('nonexistent') is False


class TestOrderAPI:
    @pytest.mark.django_db
    def test_create_order_requires_auth(self, api_client):
        """未认证不能创建订单 → 返回 401"""
        resp = api_client.post('/api/v1/order/pay/', {
            'subject': 'test', 'total_amount': '50.00',
            'pay_type': 1, 'courses': [],
        })
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_order_success_callback(self, api_client, order_data):
        """同步回调：已支付订单 → 返回成功"""
        order_data['order'].order_status = 1
        order_data['order'].save()
        # 前端在支付宝支付完成后，带 out_trade_no 调这个接口二次验证
        resp = api_client.get('/api/v1/order/success/?out_trade_no=test_order_001')
        assert resp.data['status'] == 100
        assert '支付成功' in resp.data['msg']

    @pytest.mark.django_db
    def test_order_success_callback_unpaid(self, api_client, order_data):
        """同步回调：未支付订单 → 返回未支付"""
        resp = api_client.get('/api/v1/order/success/?out_trade_no=test_order_001')
        assert resp.data['status'] == 101
        assert '未支付' in resp.data['msg']


# ============================================================
# 测试 OrderService.cancel_order
# ============================================================

class TestOrderServiceCancel:
    @pytest.mark.django_db
    def test_cancel_success(self, order_data):
        """取消未支付订单 → 状态变为 2"""
        OrderService.cancel_order(order_data['order'].id, order_data['user'].id)
        order_data['order'].refresh_from_db()
        assert order_data['order'].order_status == 2

    @pytest.mark.django_db
    def test_cancel_already_paid(self, order_data):
        """取消已支付订单 → 抛异常"""
        from utils.exception import LuffyException
        order_data['order'].order_status = 1
        order_data['order'].save()
        with pytest.raises(LuffyException) as exc:
            OrderService.cancel_order(order_data['order'].id, order_data['user'].id)
        assert '未支付' in str(exc.value)

    @pytest.mark.django_db
    def test_cancel_not_found(self, order_data):
        """取消不存在的订单 → 抛异常"""
        from utils.exception import LuffyException
        with pytest.raises(LuffyException):
            OrderService.cancel_order(99999, order_data['user'].id)

    @pytest.mark.django_db
    def test_cancel_others_order(self, db):
        """取消别人的订单 → 抛异常"""
        from utils.exception import LuffyException
        u1 = User.objects.create_user(username='a', password='123', mobile='13900000001')
        u2 = User.objects.create_user(username='b', password='123', mobile='13900000002')
        order = Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t1', user=u1)
        with pytest.raises(LuffyException):
            OrderService.cancel_order(order.id, u2.id)


# ============================================================
# 测试订单列表 & 详情 API
# ============================================================

class TestOrderListAPI:
    @pytest.mark.django_db
    def test_list_requires_auth(self, api_client):
        """未登录 → 401"""
        resp = api_client.get('/api/v1/order/list/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_list_returns_orders(self, auth_client, test_user):
        """已登录 → 返回自己的订单"""
        teacher = Teacher.objects.create(name='T', role=0, title='讲师', brief='b', orders=1)
        course = Course.objects.create(name='C', price=Decimal('10'), teacher=teacher, orders=1)
        Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t1', user=test_user)
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.get('/api/v1/order/list/')
            assert resp.status_code == 200
            assert resp.data['count'] >= 1

    @pytest.mark.django_db
    def test_list_filter_by_status(self, auth_client, test_user):
        """按状态过滤"""
        Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t2', user=test_user, order_status=0)
        Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t3', user=test_user, order_status=1)
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.get('/api/v1/order/list/?status=0')
            assert resp.status_code == 200
            for item in resp.data['results']:
                assert item['order_status'] == 0


class TestOrderDetailAPI:
    @pytest.mark.django_db
    def test_detail_requires_auth(self, api_client, order_data):
        """未登录 → 401"""
        resp = api_client.get(f'/api/v1/order/{order_data["order"].id}/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_detail_returns_order(self, auth_client, test_user):
        """已登录 → 返回订单详情"""
        order = Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t4', user=test_user)
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.get(f'/api/v1/order/{order.id}/')
            assert resp.status_code == 200
            assert resp.data['out_trade_no'] == 't4'


class TestOrderCancelAPI:
    @pytest.mark.django_db
    def test_cancel_requires_auth(self, api_client, order_data):
        """未登录 → 401"""
        resp = api_client.post(f'/api/v1/order/{order_data["order"].id}/cancel/')
        assert resp.data['status'] == 401

    @pytest.mark.django_db
    def test_cancel_success(self, auth_client, test_user):
        """已登录取消自己的未支付订单 → 成功"""
        order = Order.objects.create(subject='s', total_amount=Decimal('10'), out_trade_no='t5', user=test_user)
        with patch('utils.authentication.cache', MagicMock(get=MagicMock(return_value=None))):
            resp = auth_client.post(f'/api/v1/order/{order.id}/cancel/')
            assert resp.data['status'] == 100
            assert '取消' in resp.data['msg']
