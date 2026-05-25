from celery import Celery


# 注意注意：
# 一、加载django配置环境
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luffy_api.setting.dev")

# 实例化得到对象（不在此处指定 broker/backend，避免导入时立即连接 Redis 导致卡住）
app = Celery('test', include=[
    'celery_task.home_task',
    'celery_task.order_task',
    'celery_task.user_task',
])
# 消息中间件 & 结果存储（通过 config 设置，延迟连接）
app.conf.broker_url = 'redis://127.0.0.1:6379/2'
app.conf.result_backend = 'redis://127.0.0.1:6379/1'
# 写好include，会去相应的py下检索任务，这些任务都被app管理

# 以后任务不写在这里了，放到单独的py文件中

# 定时任务需要写在这里

#### celery的配置信息###   djagno也有配置信息--->setting.py
# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用UTC
app.conf.enable_utc = False
### celery的配置信息---结束###

#### 定时任务
from datetime import timedelta
from celery.schedules import crontab
app.conf.beat_schedule = {
    'update_banner_5': {
        'task': 'celery_task.home_task.update_banner_list',  # 哪个任务
        'schedule': timedelta(seconds=5),  # 每5s干一次
        # 'schedule': crontab(hour=8, day_of_week=1),  # 每周一早八点
        'args': (),
    },
}