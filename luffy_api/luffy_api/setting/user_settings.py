import os

# 用户自己的配置，单独放到另一个py文件中
BANNER_COUNT = 4

# 上线后通过环境变量配置公网地址
BASE_URL = os.environ.get('BACKEND_BASE_URL', 'http://127.0.0.1:80')
LUFFY_URL = os.environ.get('FRONTEND_BASE_URL', 'http://127.0.0.1:80')

# 支付宝回调接口配置
NOTIFY_URL = BASE_URL + "/api/v1/order/success/"
RETURN_URL = LUFFY_URL + "/pay/success"
