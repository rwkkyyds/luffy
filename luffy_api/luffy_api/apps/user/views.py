from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from utils.response import APIResponse
from utils.authentication import BlacklistJWTAuthentication
from .serializer import MulLoginSerializer, SmsLoginSerializer, RegisterSerializer, ProfileSerializer, AvatarSerializer
from .models import User
from .service import UserService
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@extend_schema(tags=['用户'], summary='登出', description='将当前 JWT token 加入 Redis 黑名单，使其立即失效。')
class LogoutView(APIView):
    """POST /api/v1/user/logout/ —— 登出，将当前 token 加入 Redis 黑名单"""
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        UserService.logout(request.auth)
        return APIResponse(msg="已登出")


class TestView(APIView):
    def get(self, request):
        # create_user.delay('12222222','lqznb','lqz12345')
        ip=request.META.get('REMOTE_ADDR')
        return Response('小伙子您的ip是：%s'%ip)


@extend_schema(tags=['用户'])
class MobileView(ViewSet):
    @extend_schema(summary='检查手机号是否已注册', parameters=[OpenApiParameter(name='mobile', type=str, description='手机号码')])
    @action(methods=["GET"], detail=False)
    def check_mobile(self, request):
        mobile = request.query_params.get('mobile')
        exists = UserService.check_mobile(mobile)
        # 前端判断：status=100 手机号存在，其他值不存在
        if exists:
            return APIResponse()
        return APIResponse(status=101, msg='手机号未注册')

@extend_schema_view(
    mul_login=extend_schema(tags=['用户'], summary='多方式登录', description='支持用户名/邮箱/手机号 + 密码登录，返回 JWT token。'),
    sms_login=extend_schema(tags=['用户'], summary='短信验证码登录', description='手机号 + 验证码登录，返回 JWT token。'),
)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(GenericViewSet):
    serializer_class = MulLoginSerializer
    queryset = User

    # 两个登陆方式都写在这里面（多方式，一个是验证码登陆）
    # login不是保存，但是用post，咱们的想法是把验证逻辑写到序列化类中
    @action(methods=["post"], detail=False)
    def mul_login(self, request):
        return self._common_login(request)


    # 127.0.0.1:8000/api/v1/user/login/sms_login
    @action(methods=["post"], detail=False)
    def sms_login(self, request):
        # 默认情况下使用的序列化类使用的是MulLoginSerializer---》多方式登陆的逻辑-->不符合短信登陆逻辑
        # 再新写一个序列化类，给短信登陆用
        return self._common_login(request)
    def get_serializer_class(self):
        # 方式一：
        # if 'mul_login' in self.request.path:
        #     return self.serializer_class
        # else:
        #     return SmsLoginSerializer
        # 方式二
        if self.action=='mul_login':
            return self.serializer_class
        else:
            return SmsLoginSerializer


    def _common_login(self,request):
        try:
            # 序列化类在变
            ser = self.get_serializer(data=request.data, context={'request': request})
            ser.is_valid(raise_exception=True)  # 如果校验失败，直接抛异常，不需要加if判断了
            token = ser.context.get('token')
            username = ser.context.get('username')
            icon = ser.context.get('icon')
            return APIResponse(token=token, username=username, icon=icon)  # {code:100,msg:成功，token:dsadsf,username:lqz}
        except Exception as e:
            raise APIException(str(e))

@extend_schema(tags=['用户'])
class SendSmsView(ViewSet):
    @extend_schema(summary='发送短信验证码', parameters=[OpenApiParameter(name='phone', type=str, description='手机号码')])
    @action(methods=['GET'], detail=False)
    def send_message(self, request):
        phone = request.query_params.get('phone')
        UserService.send_sms_code(phone)
        return APIResponse(msg='短信发送成功')


@extend_schema(tags=['用户'], summary='用户注册', description='手机号 + 验证码 + 密码注册，注册成功后可通过登录接口获取 token。')
class RegisterView(GenericViewSet, CreateModelMixin):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        # 校验仍在同步做（验证码必须同步校验），通过后交给 Service 层处理
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        UserService.register(data['mobile'], data['username'], data['password'])
        return APIResponse(msg='注册成功')


@extend_schema(tags=['用户'], summary='个人信息', description='查看和修改当前用户的昵称、手机号、邮箱。需要 JWT 认证。')
class ProfileView(APIView):
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return APIResponse(data=serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse(msg='修改成功', data=serializer.data)


@extend_schema(tags=['用户'], summary='上传头像', description='上传用户头像图片。需要 JWT 认证。')
class AvatarView(APIView):
    authentication_classes = [BlacklistJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        request = self.request
        icon_url = 'http://%s/media/%s' % (request.META['HTTP_HOST'], str(request.user.icon))
        return APIResponse(msg='上传成功', icon=icon_url)



