"""
支付宝支付链路诊断脚本

用法：
    cd luffy_api
    python manage.py shell < scripts/test_alipay.py

或者：
    cd luffy_api
    python -c "import os; os.environ['DJANGO_SETTINGS_MODULE']='luffy_api.setting.dev'; import django; django.setup(); exec(open('scripts/test_alipay.py').read())"
"""

import os
import sys
import pprint
import uuid

# ── 1. 环境变量检查 ──────────────────────────────────────────
print("=" * 60)
print("1. 环境变量检查")
print("=" * 60)

vars_to_check = [
    'BACKEND_BASE_URL',
    'FRONTEND_BASE_URL',
    'ALIPAY_APP_ID',
    'ALIPAY_APP_PRIVATE_KEY',
    'ALIPAY_PUBLIC_KEY',
    'ALIPAY_SIGN_TYPE',
    'ALIPAY_DEBUG',
]

env_ok = True
for v in vars_to_check:
    val = os.environ.get(v, '')
    masked = val[:20] + '...' if len(val) > 20 else val
    if not val:
        print(f"  [未设] {v}  (将使用 pem 文件 / 代码默认值)")
    else:
        print(f"  [已设] {v} = {masked}")
print()

# ── 2. Django settings 中的回调 URL ──────────────────────────
print("=" * 60)
print("2. 回调 URL（settings）")
print("=" * 60)

from django.conf import settings

urls = {
    'DEBUG': settings.DEBUG,
    'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
    'NOTIFY_URL': settings.NOTIFY_URL,
    'RETURN_URL': settings.RETURN_URL,
    'BASE_URL': settings.BASE_URL,
    'LUFFY_URL': settings.LUFFY_URL,
}
for k, v in urls.items():
    print(f"  {k} = {v}")
print()

# ── 3. iPay 模块加载 & 密钥检查 ──────────────────────────────
print("=" * 60)
print("3. iPay 模块加载 & 密钥检查")
print("=" * 60)

from libs import iPay

print(f"  alipay 对象类型: {type(iPay.alipay).__name__}")
print(f"  APP_ID:          {iPay.alipay.appid}")
print(f"  sign_type:       {iPay.alipay.sign_type}")
print(f"  沙箱模式:         {iPay.alipay.debug}")
print(f"  gateway:          {iPay.gateway}")

app_key = iPay.alipay.app_private_key_string or ''
pub_key = iPay.alipay.alipay_public_key_string or ''
print(f"  应用私钥长度:     {len(app_key)} 字符")
print(f"  支付宝公钥长度:   {len(pub_key)} 字符")

if not app_key:
    print("  ❌ 应用私钥为空！检查 pem/app_private_key.pem 是否存在")
elif 'BEGIN' not in app_key:
    print("  ⚠️  应用私钥不包含 PEM 头，可能是 Base64 编码的")
else:
    print("  ✅ 应用私钥 PEM 格式正确")

if not pub_key:
    print("  ❌ 支付宝公钥为空！检查 pem/alipay_public_key.pem 是否存在")
elif 'BEGIN' not in pub_key:
    print("  ⚠️  支付宝公钥不包含 PEM 头，可能是 Base64 编码的")
else:
    print("  ✅ 支付宝公钥 PEM 格式正确")
print()

# ── 4. 生成支付链接（沙箱测试） ──────────────────────────────
print("=" * 60)
print("4. 生成支付链接（沙箱测试）")
print("=" * 60)

out_trade_no = uuid.uuid4().hex
total_amount = 0.01
subject = "Luffy 测试订单 - 请勿付款"

print(f"  out_trade_no:    {out_trade_no}")
print(f"  total_amount:    {total_amount}")
print(f"  subject:         {subject}")
print(f"  notify_url:      {settings.NOTIFY_URL}")
print(f"  return_url:      {settings.RETURN_URL}")
print()

try:
    order_string = iPay.alipay.api_alipay_trade_page_pay(
        out_trade_no=out_trade_no,
        total_amount=float(total_amount),
        subject=subject,
        return_url=settings.RETURN_URL,
        notify_url=settings.NOTIFY_URL,
    )
    pay_url = iPay.gateway + '?' + order_string
    print(f"  ✅ 支付链接生成成功！")
    print(f"  {pay_url[:120]}...")
    print(f"  完整长度: {len(pay_url)} 字符")
except Exception as e:
    print(f"  ❌ 生成失败: {e}")
    print(f"     检查 APP_ID / 密钥是否匹配同一个沙箱应用")
    print(f"     检查沙箱网关是否正确: {iPay.gateway}")
print()

# ── 5. 签名验证测试（模拟支付宝回调） ─────────────────────────
print("=" * 60)
print("5. 签名验证测试")
print("=" * 60)

# 用刚才生成的 order_string 模拟一个回调来测试 verify
# 注意：这里用 api_alipay_trade_query 返回的数据来测 verify 更真实，
# 但沙箱未支付的订单 query 可能返回 WAIT_BUYER_PAY
try:
    query_result = iPay.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
    print(f"  trade_query 结果: {pprint.pformat(query_result, width=100)}")
except Exception as e:
    print(f"  trade_query 失败（可能沙箱无此订单或签名错误）: {e}")
print()

# ── 6. 数据库连接检查 ────────────────────────────────────────
print("=" * 60)
print("6. 数据库连接 & Order 表检查")
print("=" * 60)

try:
    from order.models import Order
    count = Order.objects.count()
    print(f"  Order 表记录数: {count}")
    print(f"  DB 连接: ✅ 正常")
except Exception as e:
    print(f"  ❌ 数据库连接失败: {e}")
print()

# ── 7. 汇总 ──────────────────────────────────────────────────
print("=" * 60)
print("诊断结论")
print("=" * 60)
print("""
  如果步骤 4 生成链接成功 → 打开链接，在沙箱页面登录买家账号支付
  支付完成后:
  1. 浏览器自动跳回 RETURN_URL（同步） → PaySuccess.vue 二次查询
  2. 支付宝异步 POST NOTIFY_URL → 更新订单状态

  排查清单:
  ☐ BACKEND_BASE_URL 是否指向 ngrok 地址（.env 或环境变量）？
  ☐ ALLOWED_HOSTS 是否包含 '*'（dev.py 已改好）？
  ☐ Django 是否已重启（让 ALLOWED_HOSTS 生效）？
  ☐ ngrok http 8000 是否在运行？
  ☐ 沙箱 APP_ID 和 pem 密钥是否匹配同一个应用？
  ☐ 浏览器打开 http://127.0.0.1:4040 可查看 ngrok 请求日志
""")
