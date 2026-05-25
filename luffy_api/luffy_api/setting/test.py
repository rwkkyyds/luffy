"""
测试环境 Django 配置
============================================================

这个文件的作用：
  让测试跑得快、不依赖外部服务（MySQL、Redis、Celery）。

它是怎么工作的：
  1. 先 from .dev import * 导入开发环境的所有配置
  2. 然后用下面的代码"覆盖"掉不适合测试的配置
  3. pytest.ini 里指定 DJANGO_SETTINGS_MODULE = luffy_api.setting.test
     所以 pytest 运行时会用这个文件而不是 dev.py

为什么要用 SQLite 内存数据库？
  - 正常开发用 MySQL，但测试时不需要真的连 MySQL
  - SQLite 内存库（:memory:）速度极快，测试结束自动销毁
  - 每个测试用例都能拿到一个干净的数据库

为什么要 Celery eager 模式？
  - 正常情况下 Celery 任务是异步的（发到 Redis 队列，worker 去执行）
  - 测试时我们希望任务"同步"执行，这样能立即看到结果
  - CELERY_TASK_ALWAYS_EAGER = True 就是让 Celery 跳过队列直接执行
"""
from .dev import *  # noqa: F401,F403  ← 导入 dev.py 的所有配置

# ----------------------------------------------------------
# 数据库：用 SQLite 内存库替代 MySQL
# ----------------------------------------------------------
# ':memory:' 表示数据库存在内存里，不写磁盘文件
# 好处：速度快、测试结束自动清理、不需要启动 MySQL 服务
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# ----------------------------------------------------------
# Celery：同步模式（不经过 Redis）
# ----------------------------------------------------------
# ALWAYS_EAGER = True  → 任务不发到队列，直接在当前进程执行
# EAGER_PROPAGATES = True → 任务里的异常会抛出来（方便发现 bug）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ----------------------------------------------------------
# 日志：测试时只输出 WARNING 以上级别到终端
# ----------------------------------------------------------
# 正常开发会写日志文件，测试时不需要
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# ----------------------------------------------------------
# 其他测试友好配置
# ----------------------------------------------------------
# DEBUG = False → 获得标准的错误处理行为（和生产环境一致）
DEBUG = False
# ALLOWED_HOSTS = ['*'] → 测试客户端的 host 不在白名单会报错，这里放行
ALLOWED_HOSTS = ['*']
# 关闭密码校验 → 测试时不需要符合复杂度要求的密码
AUTH_PASSWORD_VALIDATORS = []
