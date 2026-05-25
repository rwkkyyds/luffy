from .celery import app


@app.task
def send_sms(phone, code):
    from libs import tencent_sms_v3
    return tencent_sms_v3.send_sms(phone, code)


@app.task
def create_user(mobile, username, password):
    # password 在视图层已经用 make_password() 加密过了，是哈希密文
    # 所以这里用 User.objects.create() 直接入库
    # 不能用 create_user()，因为 create_user 会再加密一次，导致密码对不上
    from user.models import User
    User.objects.create(mobile=mobile, username=username, password=password)
    return True