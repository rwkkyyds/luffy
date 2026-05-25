/**
 * 后端 ImageField / 序列化时常返回：
 * - 相对路径：`/media/banner/xxx.png`（同源即可）
 * - 绝对路径：`http://127.0.0.1:8000/media/...`（开发时页面在 :8080，<img> 直连 :8000 易因网关/防火墙/ Referrer 出问题）
 *
 * 开发环境把本机 Django 发出的 /media URL 转成仅 path，沿用 vue.config.js 里对 `/media` 的 proxy。
 */
export function normalizeMediaSrc (raw) {
    if (raw == null || raw === '') return ''
    const s = String(raw).trim()
    const dev = process.env.NODE_ENV === 'development'

    if (dev && /^https?:\/\//i.test(s)) {
        try {
            const u = new URL(s)
            const h = u.hostname.toLowerCase()
            if ((h === '127.0.0.1' || h === 'localhost') && u.pathname.startsWith('/media')) {
                return `${u.pathname}${u.search}`
            }
        } catch (_) {
            /* ignore */
        }
    }
    if (s.startsWith('/')) return s
    if (s.startsWith('media/')) return `/${s}`
    if (!s.startsWith('http')) return `/media/${s}`
    return s
}

/**
 * 解析后端返回的错误 msg，转成用户可读的纯文本。
 *
 * 后端返回 format:
 *   纯字符串 → "该课程已在购物车中"
 *   DRF 错误 → "{'mobile': [ErrorDetail(string='手机号不合法', code='invalid')]}"
 *              "{'non_field_errors': [ErrorDetail(string='验证码错误', code='invalid')]}"
 */
export function parseErrorMsg (msg) {
    if (!msg) return '请求失败'
    if (typeof msg !== 'string' || !msg.startsWith('{')) return msg
    const texts = []
    for (const m of msg.matchAll(/string=['"]([^'"]+)['"]/g)) {
        texts.push(m[1])
    }
    return texts.length ? [...new Set(texts)].join('；') : msg
}
