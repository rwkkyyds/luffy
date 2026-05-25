from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CartView

router = SimpleRouter()
router.register('', CartView, 'cart')

urlpatterns = [
    path('', include(router.urls)),
]
