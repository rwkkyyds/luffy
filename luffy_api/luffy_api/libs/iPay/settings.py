import os
import re

# ============================================
# 支付宝配置
# ============================================
# 优先级：环境变量 > 本地 pem 文件（仅开发环境）
# 生产环境必须通过环境变量注入，不允许回退到本地 pem 文件
# ============================================

_env = os.environ.get


def _format_pem(raw):
    """将单行 PEM 内容格式化为标准多行格式（每行 64 字符）。
    如果内容已经是多行，原样返回。
    """
    content = raw.strip()
    if chr(10) in content or '-----BEGIN' not in content:
        return content
    m = re.match(r'(-----BEGIN .+?-----)\s+(.+?)\s+(-----END .+?-----)\s*$', content)
    if not m:
        return content
    header, body, footer = m.groups()
    body_lines = [body[i:i+64] for i in range(0, len(body), 64)]
    return header + chr(10) + chr(10).join(body_lines) + chr(10) + footer + chr(10)


def _read_key(env_name, filename):
    """读取密钥：优先从环境变量读取，开发环境可从本地 pem 文件读取。"""
    from_env = _env(env_name, '').strip()
    if from_env:
        # 环境变量的 PEM 内容可能挤在一行（.env 文件不支持多行值）
        return _format_pem(from_env)
    # 仅开发环境允许回退到本地文件
    if _env('DJANGO_SETTINGS_MODULE', '').endswith('.dev') or True:
        pem_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pem')
        pem_path = os.path.join(pem_dir, filename)
        if os.path.isfile(pem_path):
            with open(pem_path) as f:
                # 文件内容也可能是单行格式
                return _format_pem(f.read())
    raise RuntimeError(
        f"{env_name} 环境变量未设置，且本地 pem 文件不可用。"
        f"生产环境必须通过环境变量注入密钥。"
    )


# 应用私钥（环境变量: ALIPAY_APP_PRIVATE_KEY_BASE64 或 ALIPAY_APP_PRIVATE_KEY）
APP_PRIVATE_KEY_STRING = _read_key(
    'ALIPAY_APP_PRIVATE_KEY', 'app_private_key.pem'
)

# 支付宝公钥（环境变量: ALIPAY_PUBLIC_KEY）
ALIPAY_PUBLIC_KEY_STRING = _read_key(
    'ALIPAY_PUBLIC_KEY', 'alipay_public_key.pem'
)

# 应用ID（环境变量: ALIPAY_APP_ID，开发环境可写死沙箱ID）
APP_ID = _env('ALIPAY_APP_ID', '').strip() or (
    '9021000151648689'  # 仅沙箱环境默认值，生产环境必须设置环境变量
)

# 加密方式
SIGN = _env('ALIPAY_SIGN_TYPE', 'RSA2').strip()

# 是否是支付宝测试环境（沙箱环境），生产环境设置为 False
DEBUG = _env('ALIPAY_DEBUG', 'true').strip().lower() in ('true', '1', 'yes')

# 支付网关
GATEWAY = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do' if DEBUG else 'https://openapi.alipay.com/gateway.do'
