import logging
from django.views.decorators.csrf import csrf_exempt
from utils.response import APIResponse
from .serializer import OrderSerializer, OrderReadSerializer
from .service import OrderService
from .models import Order
from course.pagination import CommonPageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.authentication import BlacklistJWTAuthentication
from drf_spectacular.utils import extend_schema


logger = logging.getLogger('django')


@extend_schema(tags=['订单'], summary='创建订单', description='提交课程列表和总价，生成支付宝支付链接。需要 JWT 认证。')
class OrderView(GenericViewSet, CreateModelMixin):
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = OrderSerializer.Meta.model.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        pay_url = serializer.context.get('pay_url')
        self.perform_create(serializer)
        return APIResponse(pay_url=pay_url)


@extend_schema(tags=['订单'], summary='支付回调')
class SuccessViewSet(APIView):
    """支付宝回调接口"""
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        """同步回调：前端二次验证订单是否已支付"""
        out_trade_no = request.query_params.get('out_trade_no')
        if OrderService.check_order_paid(out_trade_no):
            return APIResponse(status=100, msg='订单支付成功')
        return APIResponse(status=101, msg='订单还未支付')

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """异步回调：支付宝通知后台更新订单状态"""
        try:
            result_data = request.data.dict()
            logger.warning('支付宝异步回调收到: %s', result_data)
            if OrderService.handle_alipay_callback(result_data):
                return Response('success')
        except Exception as e:
            logger.exception('支付宝异步回调处理异常: %s', e)
        return Response('failed')


# ==================== 订单列表 & 详情（新增） ====================

@extend_schema(tags=['订单'], summary='我的订单列表', description='分页返回当前用户的订单列表，支持按状态过滤。需要 JWT 认证。')
class OrderListView(GenericViewSet, ListModelMixin):
    """
    GET /api/v1/order/list/        → 当前用户的订单列表（分页）
    GET /api/v1/order/list/?status=0 → 按状态过滤（0未支付 1已支付 2已取消）
    """
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderReadSerializer
    pagination_class = CommonPageNumberPagination

    def get_queryset(self):  #get_queryset 是 DRF 固定方法，用来定义接口返回的数据列表。
        qs = (Order.objects.filter(user=self.request.user)
              .select_related('user')                      # 一对一 JOIN
              .prefetch_related('order_details__course')   # 一对多两层预取：order_details 是 OrderDetail 的 related_name，course 是 OrderDetail 的外键字段
              .order_by('-created_time'))
        # 可选的状态过滤参数
        status = self.request.query_params.get('status')
        if status is not None and status != '':
            qs = qs.filter(order_status=status)
        return qs


@extend_schema(tags=['订单'], summary='订单详情', description='返回单个订单的完整信息（含课程明细）。需要 JWT 认证。')
class OrderDetailView(GenericViewSet, RetrieveModelMixin):
    """GET /api/v1/order/<pk>/ → 单个订单详情（含课程列表）"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderReadSerializer

    def get_queryset(self):
        # 只能查自己的订单（user=self.request.user 防止越权）
        return (Order.objects.filter(user=self.request.user)
                .select_related('user')                      # 一对一：SQL JOIN，一次查询拿 Order+User
                .prefetch_related('order_details__course'))  # 一对多：两次查询+Python拼接，拿 OrderDetail→Course
    
#  拆开看 order_details__course 这条链：
#   Order  ——  order_details  ——>  OrderDetail  ——  course  ——>  Course
#             (反向，一对多)                    (正向，多对一)
#   - order_details：一个 Order 有多个 OrderDetail → 一对多 → prefetch_related 处理
#   - __course：一个 OrderDetail 只对应一个 Course → 多对一 → 直接跟外键取

@extend_schema(tags=['订单'], summary='取消订单', description='取消未支付的订单（幂等）。需要 JWT 认证。')
class OrderCancelView(APIView):
    """POST /api/v1/order/<pk>/cancel/ → 取消未支付的订单"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        OrderService.cancel_order(order_id=pk, user_id=request.user.id)
        return APIResponse(msg="订单已取消")