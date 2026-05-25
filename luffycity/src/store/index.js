import Vue from 'vue'
import Vuex from 'vuex'
import cookies from 'vue-cookies'

Vue.use(Vuex)

/**
 * 解码 JWT payload 并返回 exp（秒级时间戳），解析失败返回 0
 */
function _getJwtExp (token) {
    if (!token) return 0
    try {
        return JSON.parse(atob(token.split('.')[1])).exp || 0
    } catch {
        return 0
    }
}

function _isJwtExpired (token) {
    return !token || Date.now() >= _getJwtExp(token) * 1000
}

/** 初始化 auth 状态：从 cookie 读取，但跳过过期 token */
function _initAuth () {
    const token = cookies.get('token') || ''
    if (_isJwtExpired(token)) {
        cookies.remove('token')
        cookies.remove('username')
        cookies.remove('icon')
        return { token: '', username: '', icon: '', exp: 0 }
    }
    const icon = cookies.get('icon')
    return {
        token,
        username: cookies.get('username') || '',
        icon: icon && icon !== 'null' ? icon : '',
        exp: _getJwtExp(token),
    }
}

const _auth = _initAuth()

const store = new Vuex.Store({
    state: {
        token: _auth.token,
        username: _auth.username,
        icon: _auth.icon,
        cartCount: 0,
    },
    getters: {
        isLoggedIn: state => !!state.token,
    },
    mutations: {
        SET_USER (state, { token, username, icon }) {
            state.token = token || ''
            state.username = username || ''
            state.icon = icon ? String(icon) : ''
            cookies.set('token', state.token, '7d')
            cookies.set('username', state.username, '7d')
            cookies.set('icon', state.icon, '7d')
        },
        CLEAR_USER (state) {
            state.token = ''
            state.username = ''
            state.icon = ''
            cookies.remove('token')
            cookies.remove('username')
            cookies.remove('icon')
        },
        SET_CART_COUNT (state, count) {
            state.cartCount = Number(count) || 0
        },
    },
    actions: {},
    modules: {},
})

// token 过期时自动清除（页面长时间打开不刷新的场景）
if (_auth.exp > 0) {
    const ms = _auth.exp * 1000 - Date.now()
    if (ms > 0) {
        setTimeout(() => {
            store.commit('CLEAR_USER')
        }, ms)
    }
}

export default store
