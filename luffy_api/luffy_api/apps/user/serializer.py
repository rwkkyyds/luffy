from .models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.cache import cache
import re


# 这个序列化类，只用来做反序列化，数据校验，最后不保存，不用来做序列化
class MulLoginSerializer(serializers.ModelSerializer):
    # 一定要重写username这个字段，因为username这个字段校验规则是从User表映射过来的，
    # username是唯一，假设数据库中存在lqz这个用户，传入lqz，字段自己的校验规则就会校验失败，失败原因是数据库存在一个lqz用户了
    # 所以需要重写这个字段，取消 掉它的unique
    username = serializers.CharField(max_length=18, min_length=3)  # 一定要重写，不重写，字段自己的校验过不去，就到不了全局钩子

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, attrs):
        # 在这里面完成校验，如果校验失败，直接抛异常
        # 1 多方式得到user
        user = self._get_user(attrs)
        # 2  user签发token
        token = self._get_token(user)
        # 3  把token,username,icon放到context中
        self.context['token'] = token
        self.context['username'] = user.username
        # self.context['icon'] = 'http://127.0.0.1:8000/media/'+str(user.icon)  # 对象ImageField的对象
        # self.context['icon'] = 'http://127.0.0.1:8000/media/'+str(user.icon)  # 对象ImageField的对象
        request = self.context['request']
        # request.META['HTTP_HOST']取出服务端的ip地址
        icon = 'http://%s/media/%s' % (request.META['HTTP_HOST'], str(user.icon))
        self.context['icon'] = icon
        return attrs

    # 意思是该方法只在类内部用，但是外部也可以用，如果写成__就只能再内部用了
    def _get_user(self, attrs):
        import re
        username = attrs.get('username')
        if re.match(r'^1[3-9][0-9]{9}$', username):
            user = User.objects.filter(mobile=username).first()
        elif re.match(r'^.+@.+$', username):
            user = User.objects.filter(email=username).first()
        else:
            user = User.objects.filter(username=username).first()

        if not user:
            # raise ValidationError('用户不存在')
            raise ValidationError('用户名或密码错误')

        # 取出前端传入的密码
        password = attrs.get('password')
        if not user.check_password(password):  # 学auth时讲的，通过明文校验密码
            raise ValidationError("用户名或密码错误")

        return user

    def _get_token(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)


# 只用来做反序列化，短信登陆
class SmsLoginSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4, min_length=4)  # 字段自己的规则
    mobile = serializers.CharField(max_length=11, min_length=11)  # 一定要重写，不重写，字段自己的校验过不去，就到不了全局钩子

    class Meta:
        model = User
        fields = ['mobile', 'code']  # code不在表中，它是验证码，要重新

    def validate(self, attrs):
        # 1 验证手机号是否和合法 验证code是否合法---》去缓存中取出来判断
        self._check_code(attrs)
        # 2 根据手机号获取用户---》需要密码吗？不需要
        user = self._get_user(attrs)
        # 3 签发token
        token = self._get_token(user)
        # 4 把token，username，icon放到context中
        request = self.context['request']
        self.context['token'] = token
        self.context['username'] = user.username
        self.context['icon'] = 'http://%s/media/%s' % (request.META['HTTP_HOST'], str(user.icon))
        return attrs

    def _check_code(self, attrs):
        mobile = attrs.get('mobile')
        new_code = attrs.get('code')
        if mobile:
            # 验证验证码是否正确
            old_code = cache.get('sms_cache_%s' % mobile)
            # 置空
            if new_code != old_code:
                raise ValidationError('验证码错误')

        else:
            raise ValidationError('手机号没有带')

    def _get_user(self, attrs):
        mobile = attrs.get('mobile')
        # return User.objects.get(mobile=mobile)
        user = User.objects.filter(mobile=mobile).first()
        if user:
            return user
        else:
            raise ValidationError("该用户不存在")

    def _get_token(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)


# 主要用来做反序列化，数据校验----》其实序列化是用不到的，但是create源码中只要写了serializer.data，就会用序列化
class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4, min_length=4, write_only=True)

    class Meta:
        model = User
        fields = ['mobile', 'code', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        # 1 校验手机号和验证码
        self._check_code(attrs)
        # 2 就可以新增了---》User中字段很多，现在只带了俩字段，
        #   username必填随机生成，code不存表，剔除，
        #  存user表，不能使用默认的create，一定要重写create方法
        self._per_save(attrs)
        return attrs

    # 校验手机号
    def validate_mobile(self, value):  # 局部钩子
        if not re.match(r'^1[3-9][0-9]{9}$', value):
            raise ValidationError('手机号不合法')
        return value

    # 入库前准备
    def _per_save(self, attrs):
        # 剔除code，
        attrs.pop('code')
        # 新增username-->用手机号作为用户名
        attrs['username'] = attrs.get('mobile')

    # 写成公共函数，传入手机号，就校验验证码
    # 经常公司中为了省短信，回留万能验证码，8888
    def _check_code(self, attrs):
        # 校验code
        new_code = attrs.get('code')
        mobile = attrs.get('mobile')
        old_code = cache.get('sms_cache_%s' % mobile)
        if new_code != old_code:
            raise ValidationError("验证码错误")

    def create(self, validated_data):
        # 如果补充些，密码不是密文
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """用户个人信息（读 + 改）"""
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'icon']
        read_only_fields = ['id', 'icon']

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise ValidationError('手机号格式不正确')
        return value


class AvatarSerializer(serializers.ModelSerializer):
    """头像上传"""
    class Meta:
        model = User
        fields = ['icon']
    





    
