/**
 * Axios / fetch 使用的 API 根路径（末尾保留 /，便于与相对 path 拼接）。
 *
 * 开发环境默认 `/api/v1/`：请求发给当前页所在源（如 :8080），由 vue.config.js 的 devServer.proxy
 * 转发到 Django（:8000）。这样即使后端未启动也不会在浏览器里表现为直连 8000 的连接拒绝
 *（会先看到 dev server 侧的代理错误；后端启动后即可通）。
 *
 * 若在开发时要直连 Django，在 .env.development 里设置：
 * VUE_APP_API_BASE_URL=http://127.0.0.1:8000/api/v1/
 */
function resolveApiBaseUrl () {
    const raw = (process.env.VUE_APP_API_BASE_URL || '').trim()
    if (raw) {
        return raw.endsWith('/') ? raw : `${raw}/`
    }
    if (process.env.NODE_ENV === 'development') {
        return '/api/v1/'
    }
    return 'http://127.0.0.1:8000/api/v1/'
}

/**
 * SSE 流式接口的根路径。
 * 开发环境下直接请求 Django（跳过 webpack-dev-server proxy，因为代理会缓冲 SSE 响应）。
 * 生产环境与 base_url 相同（同源，由 nginx 代理）。
 */
function resolveStreamBaseUrl () {
    const raw = (process.env.VUE_APP_STREAM_BASE_URL || '').trim()
    if (raw) {
        return raw.endsWith('/') ? raw : `${raw}/`
    }
    if (process.env.NODE_ENV === 'development') {
        return 'http://127.0.0.1:8000/api/v1/'
    }
    return resolveApiBaseUrl()
}

export default {
    base_url: resolveApiBaseUrl(),
    stream_base_url: resolveStreamBaseUrl(),
}
