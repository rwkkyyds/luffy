from django.db import models

from user.models import User
from course.models import Course


class Order(models.Model):
    """订单模型"""
    status_choices = (
        (0, '未支付'),
        (1, '已支付'),
        (2, '已取消'),
        (3, '超时取消'),
    )
    pay_choices = (
        (1, '支付宝'),
        (2, '微信支付'),
    )
    # 订单标题
    subject = models.CharField(max_length=150, verbose_name="订单标题")
    # 总价格
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总价", default=0)
    # 订单号--使用uuid生成
    out_trade_no = models.CharField(max_length=64, verbose_name="订单号", unique=True)
    # 流水号支付宝返回的
    trade_no = models.CharField(max_length=64, null=True, verbose_name="流水号")
    # 订单状态  待支付，已支付。。。
    order_status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="订单状态")
    # 微信，支付宝
    pay_type = models.SmallIntegerField(choices=pay_choices, default=1, verbose_name="支付方式")
    # 支付时间--》支付宝回调回来会有
    pay_time = models.DateTimeField(null=True, verbose_name="支付时间")
    # 用户表关联
    user = models.ForeignKey(User, related_name='order_user', on_delete=models.DO_NOTHING, db_constraint=False,
                             verbose_name="下单用户")
    # 订单创建时间  auto_now_add:新增这个时间可以不传，用当前时间   auto_now：修改时间不传，自动存入当前时间
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = "luffy_order"
        verbose_name = "订单记录"
        verbose_name_plural = "订单记录"

    def __str__(self):
        return "%s - ￥%s" % (self.subject, self.total_amount)

    @property
    def courses(self):
        data_list = []
        for item in self.order_details.all():
            data_list.append({
                "id": item.id,
                "course_name": item.course.name,
                "real_price": item.real_price,
            })
        return data_list


class OrderDetail(models.Model):
    """订单详情"""
    # 跟订单一对多
    order = models.ForeignKey(Order, related_name='order_details', on_delete=models.CASCADE, db_constraint=False,
                              verbose_name="订单")
    # 跟课程一对多
    course = models.ForeignKey(Course, related_name='course_orders', on_delete=models.CASCADE, db_constraint=False,
                               verbose_name="课程")
    # 价格
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程原价")
    # 真实价格
    real_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程实价")

    class Meta:
        db_table = "luffy_order_detail"
        verbose_name = "订单详情"
        verbose_name_plural = "订单详情"

    def __str__(self):
        try:
            return "%s的订单：%s" % (self.course.name, self.order.out_trade_no)
        except:
            return super().__str__()
