from django.utils import timezone
from utils.log import logger
from utils.exception import LuffyException
from .models import Order


class OrderService:
    """订单业务逻辑层"""

    @classmethod
    def check_order_paid(cls, out_trade_no):
        """检查订单是否已支付，返回 True/False"""
        return Order.objects.filter(
            out_trade_no=out_trade_no, order_status=1
        ).exists()

    @classmethod
    def handle_alipay_callback(cls, result_data):
        """
        处理支付宝异步回调：
        1. 验证签名（防止伪造）
        2. 条件更新订单状态（幂等：只有未支付的才更新）
        3. 记录支付宝流水号和支付时间

        返回 True 表示处理成功，False 表示失败
        """
        out_trade_no = result_data.get('out_trade_no')
        signature = result_data.pop('sign')

        from libs import iPay
        result = iPay.alipay.verify(result_data, signature)

        if result and result_data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            trade_no = result_data.get('trade_no')
            # 条件更新实现幂等：仅"未支付(0)"时才允许更新为"已支付(1)"
            Order.objects.filter(
                out_trade_no=out_trade_no, order_status=0
            ).update(
                order_status=1,
                trade_no=trade_no,
                pay_time=timezone.now()
            )
            logger.warning('%s订单支付成功，支付宝流水号：%s' % (out_trade_no, trade_no))
            return True
        else:
            logger.error('%s订单支付失败' % out_trade_no)
            return False

    @classmethod
    def cancel_order(cls, order_id, user_id):
        """
        取消未支付的订单（幂等）
        - 只允许取消自己的订单（user_id 过滤）
        - 只有 order_status=0（未支付）才能取消 → 改为 2（已取消）
        """
        order = Order.objects.filter(id=order_id, user_id=user_id).first()
        if not order:
            raise LuffyException(msg="订单不存在", status=404)
        if order.order_status != 0:
            raise LuffyException(msg="只有未支付的订单才能取消", status=422)
        order.order_status = 2
        order.save(update_fields=['order_status'])
