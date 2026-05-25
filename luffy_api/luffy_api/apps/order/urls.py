from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import OrderView, SuccessViewSet, OrderListView, OrderDetailView, OrderCancelView

router = SimpleRouter()
router.register('pay', OrderView, 'pay')
router.register('list', OrderListView, 'order-list')  # 订单列表（分页+状态过滤）

urlpatterns = [
    path('', include(router.urls)),
    path('success/', SuccessViewSet.as_view()),
    # 用 path 而非 router.register，因为 SimpleRouter 的保留名（list/create）会冲突
    path('<int:pk>/', OrderDetailView.as_view({'get': 'retrieve'}), name='order-detail'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]
