import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR) # /Users/liuqingzheng/luffy_api/luffy_api

# 把apps的路径加入到环境变量了
sys.path.append(os.path.join(BASE_DIR, 'apps'))
# 把 小luffy_api也就是BASE_DIR 也加入到环境变量
sys.path.append(BASE_DIR)

# print(sys.path)
LUFFY_API_ROOT = os.path.dirname(BASE_DIR)

from corsheaders.defaults import default_headers as _default_cors_headers

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    ')xdu2e@a(^1p5ohypkgtft19v*5slt(-m_$gd_o637%^a3f^m(',
)

ZHIPU_API_KEY = os.environ.get('ZHIPU_API_KEY', '').strip()

_course_vec_env = os.environ.get('COURSE_VECTOR_FILE', '').strip()
COURSE_VECTOR_FILE = _course_vec_env or os.path.join(
    LUFFY_API_ROOT, 'data', 'course_vectors.json'
)

DEBUG = False

# 服务端地址 ，* 表示任意地址都可以
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'www.luffycity.com').split(',')

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',  # OpenAPI 3.0 文档自动生成
    'corsheaders',
    # 'luffy_api.apps.user' # 太长，我们不喜欢
    'user',
    'home',
    'course',
    'django_filters',
    'order',
    'ai',
    'cart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.request_log.RequestLogMiddleware',  # 请求/响应日志
]

ROOT_URLCONF = 'luffy_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'luffy_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# 在这，用户名和密码都能看到---》万一你的代码泄露了---》数据库的用户名密码就泄露了--》不安全
# django---》监控公司代码是否被传到github，gitee--》
# B站的go源代码泄露---->某个人传到了github
# 拖库---》华住汉庭酒店---》20g开房数据泄露
# 把密码不写死在源文件中，而从环境变量中取
pwd = os.environ.get("PASSWORD", "Luffy123?")
# # 单独有接口，向接口发送请求，获取到密码---》自己做的
# pwd=requests.get().json()['password']
# # 配置中心 Apollo--公司自己搭建的

_mysql_port = os.environ.get('MYSQL_PORT', '3306')
try:
    _mysql_port = int(_mysql_port)
except ValueError:
    _mysql_port = 3306

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'luffy'),
        'USER': os.environ.get('MYSQL_USER', 'luffy'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', pwd),
        'HOST': os.environ.get('MYSQL_HOST', 'luffy_mysql'),
        'PORT': _mysql_port,
    }
}
# 这两句话，只要执行即可，放在那里都行---》只要django执行，所有py文件中顶格写的代码都会执行
# 作用是？猴子补丁，动态替换  --->python一切皆对象，可以动态替换对象
# 如果该源码，后期只要使用django，都要改它的源码
# 所以咱们换另一个操作mysql的模块，mysqlclient
# import pymysql
# pymysql.install_as_MySQLdb()


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/


LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# # 日志相关
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            # 实际开发建议使用WARNING
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            # 实际开发建议使用ERROR
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # 日志位置,日志文件名,日志保存目录必须手动创建，注：这里的文件路径要注意BASE_DIR代表的是小luffyapi
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs", "luffy.log"),
            # 日志文件的最大值,这里我们设置300M
            'maxBytes': 300 * 1024 * 1024,
            # 日志文件的数量,设置最大日志数量为10
            'backupCount': 10,
            # 日志格式:详细格式
            'formatter': 'verbose',
            # 文件内容编码
            'encoding': 'utf-8'
        },
    },
    # 日志对象
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,  # 是否让日志信息继续冒泡给其他的日志处理系统
        },
    }
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exception.common_exception_handler',  # 再出异常，会执行这个函数
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# 把扩写了auth的user表注册一下
AUTH_USER_MODEL = 'user.user'

# 配置media文件夹
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 上传文件大小限制（nginx 需同步调整 client_max_body_size）
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# 跨域问题处理
# 允许简单请求，所有地址 相当于CORS_ORIGIN_ALLOW_ALL="*"
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'https://www.luffycity.com'
).split(',')
# 运行的请求
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'POST',
    'PUT',
)

# 允许的请求头（在库默认基础上追加）
CORS_ALLOW_HEADERS = list(_default_cors_headers) + [
    'Pragma',
]

# 导入用户自定义的配置
from .user_settings import *

import datetime

# simplejwt 配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer'),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# drf-spectacular: OpenAPI 3.0 文档配置
SPECTACULAR_SETTINGS = {
    'TITLE': 'Luffy 在线教育平台 API',
    'DESCRIPTION': 'Luffy 路飞学城后端接口文档，包含用户、课程、订单、AI 问答等模块。',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'jwtAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': '用户', 'description': '登录、注册、短信、登出'},
        {'name': '首页', 'description': '轮播图'},
        {'name': '课程', 'description': '课程分类、课程列表、章节、搜索'},
        {'name': '订单', 'description': '下单、支付回调'},
        {'name': 'AI', 'description': 'AI 问答、课程 RAG 问答'},
        {'name': '系统', 'description': '健康检查'},
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'jwtAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': '输入 `jwt <token>` 或 `Bearer <token>`',
            }
        }
    },
}

# redis的配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://luffy_redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100}
            # "PASSWORD": "123",
        }
    },
}
