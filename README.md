# Luffy 在线教育平台 — Docker 部署指南

## 架构概览

```
浏览器 → Nginx(:80)
            ├── /            → Vue SPA（dist/ 静态文件）
            ├── /api/        → Django uWSGI(:8080)
            ├── /media/      → Django（用户上传的图片）
            └── /admin/      → Django Admin

Django → MySQL(:3306) + Redis(:6379)
```

## 前置条件

- Ubuntu 20.04+ 虚拟机
- Docker 20+ & Docker Compose v2
- Node.js 16+（仅构建前端时需要，构建完可卸载）

```bash
# 安装 Docker（如果没有）
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# 重新登录终端生效

# 安装 Node.js（用于构建前端）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 部署步骤

### 第 1 步：克隆代码

```bash
git clone <你的仓库地址> /root/luffy
cd /root/luffy
```

### 第 2 步：配置后端环境变量

```bash
# 复制模板
cp luffy_api/.env.example luffy_api/.env
cp docker_compose_files/mysql.env.example docker_compose_files/mysql.env
```

编辑 `luffy_api/.env`，填入真实值：

```ini
# Django 密钥（务必更换为随机字符串）
DJANGO_SECRET_KEY=<生成一个随机字符串>
# MySQL（与 mysql.env 保持一致）
MYSQL_DATABASE=luffy
MYSQL_USER=luffy
MYSQL_PASSWORD=<你的MySQL密码>
MYSQL_HOST=luffy_mysql
MYSQL_PORT=3306
PASSWORD=<与上面MYSQL_PASSWORD一致>
# 部署设置
ALLOWED_HOSTS=<你的服务器IP>
CORS_ALLOWED_ORIGINS=http://<你的服务器IP>
# 公网地址（支付宝回调用；内网穿透时 BACKEND 改 ngrok 地址）
BACKEND_BASE_URL=http://<你的服务器IP>
FRONTEND_BASE_URL=http://<你的服务器IP>
# 智谱 AI（不配的话 AI 问答返回 503）
ZHIPU_API_KEY=<你的智谱API Key>
# 支付宝（沙箱测试用 DEBUG=true；正式上线改为 false 并换正式密钥）
ALIPAY_APP_ID=<支付宝AppID>
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_DEBUG=true
# 密钥：环境变量为空时，会自动从 luffy_api/luffy_api/libs/iPay/pem/ 读取文件
# 所以不需要在这里填 ALIPAY_APP_PRIVATE_KEY 和 ALIPAY_PUBLIC_KEY
```

> **PEM 密钥说明：** 本项目 `iPay/settings.py` 内置了单行 PEM → 标准多行格式化逻辑。  
> 有两种提供密钥的方式（按优先级）：
> 1. 环境变量 `ALIPAY_APP_PRIVATE_KEY` / `ALIPAY_PUBLIC_KEY` — 支持单行
> 2. 放到 `luffy_api/luffy_api/libs/iPay/pem/` 目录 — `app_private_key.pem` + `alipay_public_key.pem`  
> 推荐用方式 2（文件），避免 .env 里混入 PEM 导致换行问题。

编辑 `docker_compose_files/mysql.env`：

```ini
MYSQL_ROOT_PASSWORD=<你的MySQL Root密码>
MYSQL_DATABASE=luffy
MYSQL_USER=luffy
MYSQL_PASSWORD=<你的MySQL密码（与上面一致）>
TZ=Asia/Shanghai
```

### 第 3 步：构建前端

```bash
cd luffycity

# 修改生产环境 API 地址
echo "VUE_APP_API_BASE_URL=http://<你的服务器IP>/api/v1/" > .env.production

# 安装依赖并构建
npm install
npm run build

cd ..
```

### 第 4 步：创建必要目录

```bash
mkdir -p luffy_api/logs
mkdir -p docker_compose_files/mysql/data
mkdir -p docker_compose_files/mysql/logs
mkdir -p docker_compose_files/mysql/conf
mkdir -p docker_compose_files/redis/data
```

### 第 5 步：启动服务

```bash
docker-compose up -d --build
```

首次启动会：

1. 构建 Django 镜像（安装 Python 依赖，约 3-5 分钟）
2. 拉取 MySQL 8.0、Redis 8.4、Nginx 镜像
3. 等待 MySQL 健康检查通过后启动 Django
4. Django 自动执行 `makemigrations` + `migrate` 建表
5. 启动 uWSGI 监听 8080 端口

### 第 6 步：初始化数据

```bash
# 创建管理员账号
docker exec -it luffy_django python manage_pro.py createsuperuser

# 导入测试数据（可选）
docker cp luffy_api/luffy.sql luffy_django:/tmp/
docker exec -i luffy_django mysql -h luffy_mysql -u luffy -p<密码> luffy < /tmp/luffy.sql
```

### 第 7 步：构建 AI 课程向量索引

AI 问答功能依赖离线构建的向量索引。导入课程数据后，在 Django 容器内执行：

```bash
# 确认 ZHIPU_API_KEY 已在 .env 中配置
docker exec -i luffy_django python scripts/build_course_vectors.py
```

该脚本会遍历所有已上架课程（`status=0`）：
- 每门课的**概述**生成一条向量
- 每个**课时**生成一条向量（精确到章节 → 课时名）
- 调用智谱 embedding-2 API 生成向量，存入 FAISS 索引
- 产出文件：`luffy_api/data/course_vectors.json` + `luffy_api/data/course_vectors.index`

> 索引文件已在 `.gitignore` 中排除，不会被提交到 Git。每次新增/修改课程后重新运行一次即可。

### 第 8 步：访问

- 前端首页：`http://<你的服务器IP>`
- 后台管理：`http://<你的服务器IP>/admin/`
- API 文档：`http://<你的服务器IP>/api/docs/`
- ReDoc：`http://<你的服务器IP>/api/redoc/`

---

## 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看 Django 日志
docker logs -f luffy_django

# 查看 Django 应用日志
tail -f luffy_api/logs/luffy.log

# 查看 uWSGI 日志
tail -f luffy_api/logs/uwsgi.log

# 查看 Nginx 日志
docker logs -f luffy_nginx

# 进入 Django 容器
docker exec -it luffy_django bash

# 重启单个服务（代码修改后）
docker-compose restart django

# 重新构建并启动
docker-compose up -d --build django

# 停止所有服务
docker-compose down

# 停止并删除数据卷（慎用！会清空数据库）
docker-compose down -v
```

---

## 目录结构

```
/root/luffy/
├── docker-compose.yml                    # 服务编排
├── docker_compose_files/
│   ├── mysql.env                         # MySQL 环境变量
│   ├── mysql.env.example                 # MySQL 环境变量模板
│   ├── mysql/                            # MySQL 数据/日志/配置
│   ├── nginx/default.conf               # Nginx 配置
│   └── redis/redis.conf                 # Redis 配置
├── luffy_api/
│   ├── .env                              # 后端环境变量（gitignore）
│   ├── .env.example                      # 环境变量模板
│   ├── Dockerfile                        # Django 镜像构建（多阶段）
│   ├── uwsgi.ini                         # uWSGI 配置
│   ├── requirements.txt                  # Python 依赖
│   ├── manage.py                         # 开发 manage.py
│   ├── manage_pro.py                     # 生产 manage.py
│   ├── logs/                             # uWSGI + Django 日志
│   ├── data/                             # RAG 向量索引文件
│   │   ├── course_vectors.json           # 向量数据（gitignore）
│   │   └── course_vectors.index          # FAISS 索引（gitignore）
│   └── luffy_api/
│       ├── setting/
│       │   ├── dev.py                    # 开发配置
│       │   ├── pro.py                    # 生产配置
│       │   └── user_settings.py          # 用户配置（回调地址等）
│       ├── apps/                         # user, home, course, order, ai, cart
│       ├── libs/
│       │   ├── iPay/                     # 支付宝 SDK
│       │   │   ├── settings.py           # 支付宝配置（自动处理单行 PEM）
│       │   │   └── pem/                  # PEM 密钥文件（gitignore）
│       │   ├── llm/                      # 智谱 AI
│       │   └── rag/                      # RAG 向量检索
│       ├── utils/
│       │   ├── csrf_middleware.py         # API CSRF 豁免中间件
│       │   ├── authentication.py         # JWT 黑名单认证
│       │   └── exception.py              # 统一异常处理
│       └── middleware/
│           └── request_log.py            # 请求/响应日志中间件
└── luffycity/
    ├── dist/                             # Vue 构建产物（挂载到 Nginx）
    ├── src/                              # 前端源码
    └── .env.production                   # 前端环境变量
```

---

## 已解决的部署问题

部署前已修复以下问题：

| #   | 问题                            | 修复                               |
| --- | ----------------------------- | -------------------------------- |
| 1   | requirements.txt 每个字符间有空格     | 重写为正常格式                          |
| 2   | pro.py INSTALLED_APPS 缺少 cart | 补上 `'cart'`                      |
| 3   | uwsgi.ini 不存在                 | 创建文件                             |
| 4   | Dockerfile CMD 引用 `luffy.ini` | 改为 `uwsgi.ini`                   |
| 5   | nginx 缺少 media 代理             | 添加 `/media/` 转发到 Django          |
| 6   | nginx SSE 流式响应被缓冲             | `/api/` 添加 `proxy_buffering off` |
| 7   | user_settings.py 硬编码 IP       | 改为读取环境变量                         |
| 8   | 登录 CSRF 403 错误               | 新增 ApiCsrfExemptMiddleware 中间件    |
| 9   | ALLOWED_HOSTS 拒绝 192.168.* 请求 | 默认值增加 192.168.10.136 等 IP       |
| 10  | 支付宝 PEM 单行格式解析失败            | iPay/settings.py 增加 `_format_pem()` 自动格式化 |
| 11  | `name 're' is not defined`    | iPay/settings.py 补上 `import re`   |
| 12  | 前端视频硬编码导致无法播放              | CourseDetail.vue mp4_url 改为空字符串   |

---

## 常见问题

**Q：MySQL 启动失败，报权限错误**

```bash
sudo chown -R 999:999 docker_compose_files/mysql/data
```

**Q：Django 连不上 MySQL**
检查 `.env` 的 `MYSQL_HOST=luffy_mysql`（是容器名，不是 localhost）。

**Q：前端页面空白**
检查 `luffycity/dist/index.html` 是否存在，没构建就执行第 3 步。

**Q：API 返回 403 Forbidden**
检查 `.env` 的 `ALLOWED_HOSTS` 和 `CORS_ALLOWED_ORIGINS`。

**Q：Nginx 报 502 Bad Gateway**
检查 Django 容器是否正常运行：`docker logs luffy_django --tail 20`。

**Q：支付宝回调失败**
`user_settings.py` 的 `BACKEND_BASE_URL` 需为公网可访问地址（内网穿透用 ngrok）。

**Q：AI 问答不工作 / 返回 503**
1. 检查 `.env` 的 `ZHIPU_API_KEY` 是否已配置且有效。
2. 确认已执行第 7 步构建向量索引（`luffy_api/data/course_vectors.json` 和 `.index` 存在）。
3. 如果仅没有索引文件，AI 仍可对话但无法检索课程内容。

**Q：Django 容器显示 unhealthy**
Dockerfile HEALTHCHECK 访问 `/health/` 路径不存在（始终 400），不影响业务功能。

**Q：PEM 密钥报 "must have at least 3 lines"**
确认 `iPay/pem/` 下的 PEM 文件是标准多行格式；或者确认 .env 中密钥变量为空（自动走文件读取）。`settings.py` 已内置 `_format_pem()` 自动修复单行格式。
