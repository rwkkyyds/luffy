# ============ 阶段1：构建阶段 ============
FROM python:3.11-slim-bookworm AS builder

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements
COPY requirements.txt /tmp/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir --prefix=/install \
    -r /tmp/requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple


# ============ 阶段2：运行阶段 ============
FROM python:3.11-slim-bookworm

LABEL maintainer="lqz"

# 安装运行依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制 Python 包
COPY --from=builder /install /usr/local

# 创建工作目录
RUN mkdir -p /soft && useradd -r -s /bin/false luffy

WORKDIR /soft

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health/')" || exit 1

# 启动 uwsgi
CMD ["uwsgi", "--ini", "/soft/uwsgi.ini"]

