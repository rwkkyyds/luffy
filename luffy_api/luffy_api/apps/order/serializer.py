from .models import Order, OrderDetail
from course.models import Course
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


#只用来做反序列化--->数据校验-->重写create方法--》存两个表
class OrderSerializer(serializers.ModelSerializer):
    # 前端传入的是课程列表[1,2,3,]---》转成[课程对象1，课程对象2，课程对象3]
    courses = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), many=True)

    # 前端传入的是课程列表[1,2,3,]
    # courses = serializers.ListField()

    class Meta:
        model = Order
        # 订单标题，总价格，支付方式，courses所有购买的课程id号列表
        fields = ('subject', 'total_amount', 'pay_type', 'courses')

    def _check_total_amount(self, attrs):
        courses = attrs.get('courses')  # 列表[课程1，课程2，课程3]
        total_amount = attrs.get('total_amount')  # 前端传入的总价格
        total_price = 0
        for course in courses:
            total_price += course.price
        if total_price != total_amount:  # 计算完的价格不等于传入的价格，抛异常
            raise ValidationError('total_amount error')
        return total_amount

    def _get_out_trade_no(self):
        import uuid
        code = str(uuid.uuid4())  # 分布式id的生成方案：订单号全局唯一，如何生成全局唯一的订单号：uuid，使用当前时间时间戳(重复概率)，雪花算法
        return code.replace('-', '')

    # 获取支付人
    def _get_user(self):
        return self.context.get('request').user

    # 获取支付链接
    def _get_pay_url(self, out_trade_no, total_amount, subject):
        from libs import iPay
        from django.conf import settings
        order_string = iPay.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=float(total_amount),  # 只有生成支付宝链接时，不能用Decimal
            subject=subject,
            return_url=settings.RETURN_URL,  # get回调地址，前台地址
            notify_url=settings.NOTIFY_URL,  # post回调地址,后台地址
        )
        pay_url = iPay.gateway + '?' + order_string
        # 将支付链接存入，传递给views
        self.context['pay_url'] = pay_url

    # 入库(两个表)的信息准备
    def _before_create(self, attrs, user, out_trade_no):
        attrs['user'] = user
        attrs['out_trade_no'] = out_trade_no

    def validate(self, attrs):
        # 1）订单总价校验--
        total_amount = self._check_total_amount(attrs)
        # 2）生成订单号--》唯一的
        out_trade_no = self._get_out_trade_no()
        # 3）支付用户：request.user
        user = self._get_user()
        # 4）支付链接生成
        self._get_pay_url(out_trade_no, total_amount, attrs.get('subject'))
        # 5）入库(两个表)的信息准备
        self._before_create(attrs, user, out_trade_no)

        # 代表该校验方法通过，进入入库操作
        return attrs

    def create(self, validated_data):
        courses = validated_data.pop('courses')
        # 订单表入库，不需要courses, 订单号，订单标题，订单价格，购买人，支付方式
        order = Order.objects.create(**validated_data)
        # 订单详情表入库：只需要订单对象，课程对象(courses要拆成一个个course)
        for course in courses:
            OrderDetail.objects.create(order=order, course=course, price=course.price, real_price=course.price)
        return order


# ==================== 订单列表 & 详情（新增） ====================
# 以下两个序列化器只用于序列化（读），不用于反序列化（写）
# 写操作仍走上面的 OrderSerializer

class OrderDetailSerializer(serializers.ModelSerializer):
    """订单中的课程信息 —— 从 OrderDetail 反向关联到 Course 拿名称和图片"""
    # source='course.name' 表示从 OrderDetail.course 外键取 course.name
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_img = serializers.ImageField(source='course.course_img', read_only=True)

    class Meta:
        model = OrderDetail
        fields = ['course', 'course_name', 'course_img', 'price', 'real_price']


class OrderReadSerializer(serializers.ModelSerializer):
    """订单列表/详情序列化器"""
    # source='get_xxx_display' 自动取 Django choice 字段的中文显示值
    status_name = serializers.CharField(source='get_order_status_display', read_only=True)
    pay_type_name = serializers.CharField(source='get_pay_type_display', read_only=True)
    # source='order_details' 是 OrderDetail 中 order 字段的 related_name
    courses = OrderDetailSerializer(source='order_details', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'subject', 'total_amount', 'out_trade_no', 'order_status',
                  'status_name', 'pay_type', 'pay_type_name', 'created_time', 'courses']
