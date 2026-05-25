import uuid
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.authentication import BlacklistJWTAuthentication
from utils.response import APIResponse
from .service import CartService
from .serializer import CartAddSerializer
from drf_spectacular.utils import extend_schema

CART_COOKIE_KEY = 'luffy_cart_id'
CART_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30天


@extend_schema(tags=['购物车'])
class CartView(GenericViewSet):
    """
    购物车视图集
    - add / list / remove / clear: 登录/未登录均可（未登录用 cookie 标识）
    - checkout: 必须登录（需要创建订单）
    """
    authentication_classes = [BlacklistJWTAuthentication]

    def _resolve_owner(self, request, response=None):
        """
        统一判断购物车归属：登录用 user_id，未登录用 cookie_id。
        如果已登录且有临时购物车 → 自动合并。
        返回：owner（int=user_id 或 str=cookie_id）
        """
        if request.user.is_authenticated:
            cookie_id = request.COOKIES.get(CART_COOKIE_KEY)
            if cookie_id:
                CartService.merge_cart(cookie_id, request.user.id)
            return request.user.id
        # 未登录：从 cookie 取或新建
        cookie_id = request.COOKIES.get(CART_COOKIE_KEY)
        if not cookie_id and response is not None:
            cookie_id = str(uuid.uuid4()).replace('-', '')
            response.set_cookie(
                CART_COOKIE_KEY, cookie_id,
                max_age=CART_COOKIE_MAX_AGE, httponly=True,
            )
        return cookie_id  # 可能是 None（无 cookie 且无法写入时）

    @extend_schema(summary='添加课程到购物车',
                   description='已登录：加入个人购物车。未登录：用 cookie 临时存储，登录后自动合并。')
    @action(methods=['post'], detail=False, url_path='add',
            permission_classes=[AllowAny])
    def add(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data['course_id']
        price = serializer.validated_data['price']

        if request.user.is_authenticated:
            owner = self._resolve_owner(request)
            count = CartService.add(owner, course_id, price)
            return APIResponse(msg="添加成功", cart_count=count)

        # 未登录：需要 response 写 cookie
        resp = APIResponse()
        owner = self._resolve_owner(request, resp)
        if owner is None:
            return APIResponse(status=400, msg="无法创建购物车")
        count = CartService.add(owner, course_id, price)
        resp.data = {'status': 100, 'msg': '添加成功', 'cart_count': count}
        return resp

    @extend_schema(summary='获取购物车列表',
                   description='已登录：返回个人购物车。未登录：返回 cookie 临时购物车。')
    @action(methods=['get'], detail=False, url_path='list',
            permission_classes=[AllowAny])
    def cart_list(self, request):
        # print('33333333333333333333333333333333333333333',request.user.is_authenticated)
        if request.user.is_authenticated:
            owner = self._resolve_owner(request)
            cart_items = CartService.list(owner)
            return APIResponse(cart_items=cart_items, cart_count=len(cart_items))

        cookie_id = request.COOKIES.get(CART_COOKIE_KEY)
        if not cookie_id:
            return APIResponse(cart_items=[], cart_count=0)
        cart_items = CartService.list(cookie_id)
        return APIResponse(cart_items=cart_items, cart_count=len(cart_items))

    @extend_schema(summary='移除购物车中的课程',
                   description='已登录：从个人购物车移除。未登录：从临时购物车移除。')
    @action(methods=['delete'], detail=False, url_path=r'remove/(?P<course_id>\d+)',
            permission_classes=[AllowAny])
    def remove(self, request, course_id=None):
        owner = self._resolve_owner(request)
        if owner is None:
            return APIResponse(status=401, msg="请先登录")
        count = CartService.remove(owner, int(course_id))
        return APIResponse(msg="移除成功", cart_count=count)

    @extend_schema(summary='清空购物车',
                   description='已登录：清空个人购物车。未登录：清空临时购物车。')
    @action(methods=['delete'], detail=False, url_path='clear',
            permission_classes=[AllowAny])
    def clear(self, request):
        owner = self._resolve_owner(request)
        if owner is None:
            return APIResponse(status=401, msg="请先登录")
        CartService.clear(owner)
        return APIResponse(msg="购物车已清空")

    @extend_schema(summary='结算购物车', description='将购物车中的课程生成订单。必须登录。')
    @action(methods=['post'], detail=False, url_path='checkout',
            permission_classes=[IsAuthenticated])
    def checkout(self, request):
        owner = request.user.id
        checkout_data = CartService.checkout(owner)

        from order.models import Order, OrderDetail
        from course.models import Course

        course_ids = checkout_data['course_ids']
        total_amount = checkout_data['total_amount']
        courses = Course.objects.filter(id__in=course_ids, is_delete=False)

        out_trade_no = str(uuid.uuid4()).replace('-', '')
        order = Order.objects.create(
            user=request.user,
            subject=f"购物车结算-{len(courses)}门课程",
            total_amount=total_amount,
            out_trade_no=out_trade_no,
            pay_type=1,
            order_status=0,
        )
        for course in courses:
            OrderDetail.objects.create(
                order=order, course=course,
                price=course.price, real_price=course.price,
            )
        CartService.clear(owner)

        from libs import iPay
        from django.conf import settings
        order_string = iPay.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=float(total_amount),
            subject=order.subject,
            return_url=settings.RETURN_URL,
            notify_url=settings.NOTIFY_URL,
        )
        pay_url = iPay.gateway + '?' + order_string

        return APIResponse(
            msg="订单创建成功",
            order_id=order.id,
            out_trade_no=out_trade_no,
            total_amount=str(total_amount),
            pay_url=pay_url,
        )
