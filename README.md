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
git clone <你的仓库地址> /home/luffy
cd /home/luffy
```

### 第 2 步：配置后端环境变量

```bash
# 复制模板
cp luffy_api/.env.example luffy_api/.env
cp docker_compose_files/mysql.env.example docker_compose_files/mysql.env
```

编辑 `luffy_api/.env`，填入真实值：

```ini
DJANGO_SECRET_KEY=换成随机字符串
MYSQL_DATABASE=luffy
MYSQL_USER=luffy
MYSQL_PASSWORD=你的MySQL密码
MYSQL_HOST=luffy_mysql
MYSQL_PORT=3306
PASSWORD=你的MySQL密码
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=*
ZHIPU_API_KEY=你的智谱API Key
BACKEND_BASE_URL=http://你的服务器IP
FRONTEND_BASE_URL=http://你的服务器IP
# 支付宝（生产环境必须用环境变量注入密钥，勿依赖 pem 文件）
# 沙箱测试保持 DEBUG=true，正式上线改为 false
ALIPAY_APP_ID=你的支付宝AppID
ALIPAY_APP_PRIVATE_KEY=你的应用私钥PEM格式
ALIPAY_PUBLIC_KEY=你的支付宝公钥PEM格式
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_DEBUG=true
```

编辑 `docker_compose_files/mysql.env`：

```ini
MYSQL_ROOT_PASSWORD=你的MySQL Root密码
MYSQL_DATABASE=luffy
MYSQL_USER=luffy
MYSQL_PASSWORD=你的MySQL密码（与上面一致）
TZ=Asia/Shanghai
```

### 第 3 步：构建前端

```bash
cd luffycity

# 修改生产环境 API 地址
echo "VUE_APP_API_BASE_URL=http://你的服务器IP/api/v1/" > .env.production

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
2. 拉取 MySQL 5.7、Redis 8.4、Nginx 镜像
3. 等待 MySQL 健康检查通过后启动 Django
4. Django 自动执行 `makemigrations` + `migrate` 建表
5. 启动 uWSGI 监听 8080 端口

### 第 6 步：初始化数据

```bash
# 创建管理员账号
docker exec -it luffy_django python manage_pro.py createsuperuser

# 导入测试数据（可选）
docker cp luffy_api/luffy.sql luffy_django:/tmp/
docker exec -it luffy_django mysql -h luffy_mysql -u luffy -p luffy < /tmp/luffy.sql
```

### 第 7 步：访问

- 前端首页：`http://你的服务器IP`
- 后台管理：`http://你的服务器IP/admin/`
- API 文档：`http://你的服务器IP/api/docs/`
- Swagger：`http://你的服务器IP/api/swagger/`

---

## 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看 Django 日志
docker logs -f luffy_django

# 查看 Nginx 日志
docker logs -f luffy_nginx

# 进入 Django 容器
docker exec -it luffy_django bash

# 重启单个服务
docker-compose restart django

# 重新构建并启动（代码变更后）
docker-compose up -d --build django

# 停止所有服务
docker-compose down

# 停止并删除数据卷（慎用！会清空数据库）
docker-compose down -v
```

---

## 目录结构

```
/home/luffy/
├── docker-compose.yml                    # 服务编排
├── docker_compose_files/
│   ├── mysql.env                         # MySQL 环境变量
│   ├── mysql/                            # MySQL 数据/日志/配置
│   ├── nginx/default.conf               # Nginx 配置
│   └── redis/redis.conf                 # Redis 配置
├── luffy_api/
│   ├── .env                              # 后端环境变量
│   ├── Dockerfile                        # Django 镜像构建
│   ├── uwsgi.ini                         # uWSGI 配置
│   ├── requirements.txt                  # Python 依赖
│   ├── manage_pro.py                     # 生产 manage.py
│   ├── logs/                             # uWSGI + Django 日志
│   └── luffy_api/setting/
│       ├── pro.py                        # 生产配置
│       └── user_settings.py             # 用户配置（回调地址等）
└── luffycity/
    ├── dist/                             # Vue 构建产物（挂载到 Nginx）
    └── src/                              # 前端源码
```

---

## 已修复的部署问题

部署前已修复以下问题：

| # | 问题 | 修复 |
|---|------|------|
| 1 | requirements.txt 每个字符间有空格 | 重写为正常格式 |
| 2 | pro.py INSTALLED_APPS 缺少 cart | 补上 `'cart'` |
| 3 | uwsgi.ini 不存在 | 创建文件 |
| 4 | Dockerfile CMD 引用 `luffy.ini` | 改为 `uwsgi.ini` |
| 5 | nginx 缺少 media 代理 | 添加 `/media/` 转发到 Django |
| 6 | nginx SSE 流式响应被缓冲 | `/api/` 添加 `proxy_buffering off` |
| 7 | user_settings.py 硬编码 IP | 改为读取环境变量 |

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
检查 `.env` 的 `ALLOWED_HOSTS=*` 和 `CORS_ALLOWED_ORIGINS=*`。

**Q：支付宝回调失败**
`user_settings.py` 的 `BACKEND_BASE_URL` 需为公网可访问地址。

**Q：AI 问答不工作**
检查 `.env` 的 `ZHIPU_API_KEY` 是否已配置。

**Q：导入 SQL 时报错**
`luffy.sql` 可能含有已存在的数据，用 Navicat 远程连接 MySQL 导入即可。
