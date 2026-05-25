
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import MobileView,LoginView,SendSmsView,RegisterView,TestView,LogoutView,ProfileView,AvatarView

router = SimpleRouter()
# 127.0.0.1:8000/api/v1/user/mobile/check_mobile
router.register('mobile',MobileView , 'mobile')
# # 127.0.0.1:8000/api/v1/user/login/mul_login/--->post
router.register('login',LoginView , 'login')
# 127.0.0.1:8000/api/v1/user/send/send_message/--->get
router.register('send',SendSmsView , 'send')
# 127.0.0.1:8000/api/v1/user/register --- >post请求
router.register('register',RegisterView , 'register')
urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('avatar/', AvatarView.as_view(), name='user-avatar'),
]
