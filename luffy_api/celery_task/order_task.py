
from .celery import app
@app.task
def order_update():
    print('订单生成了')
    return  '订单生成了'