import axios from 'axios'
import router from '@/router'
import cookies from 'vue-cookies'
import { Message } from 'element-ui'
import settings from '@/assets/js/settings'
import store from '@/store'
import { parseErrorMsg } from '@/utils/media'

const http = axios.create({
    baseURL: settings.base_url,
    timeout: 30000,
    withCredentials: true,
})

http.interceptors.request.use(
    config => {
        const token = store.state.token || cookies.get('token')
        if (token) {
            config.headers.Authorization = `jwt ${token}`
        }
        return config
    },
    error => Promise.reject(error)
)

// 统一处理后端返回的 msg：DRF 错误字典 → 可读文本
function normalizeMsg (msg) {
    const clean = parseErrorMsg(msg)
    return clean || msg
}

http.interceptors.response.use(
    response => {
        if (response.data && typeof response.data.msg === 'string') {
            response.data.msg = normalizeMsg(response.data.msg)
        }
        return response
    },
    error => {
        const status = error.response?.status
        if (status === 401) {
            store.commit('CLEAR_USER')
            if (router.currentRoute.name !== 'login') {
                Message.warning(error.response?.data?.msg || '登录已失效，请重新登录')
                router.replace({ path: '/home' }).catch(() => {})
            }
        } else if (status === 429) {
            Message.warning(error.response?.data?.msg || '请求过于频繁，请稍后重试')
        } else if (status >= 500) {
            Message.error('服务暂时不可用，请稍后再试')
        }
        return Promise.reject(error)
    }
)


export default http
