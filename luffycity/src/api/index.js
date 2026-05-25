/**
 * Central API paths (relative to VUE_APP_API_BASE_URL via http baseURL).
 * Keep URLs in one place for backend path changes.
 */
import http from '@/utils/http'

export const api = {
    home: {
        banner: () => http.get('home/banner/'),
    },
    user: {
        logout: () => http.post('user/logout/', {}),
        sendSms: phone => http.get(`user/send/send_message/?phone=${encodeURIComponent(phone)}`),
        loginMul: data => http.post('user/login/mul_login/', data),
        loginSms: data => http.post('user/login/sms_login/', data),
        register: data => http.post('user/register/', data),
        profile: () => http.get('user/profile/'),
        updateProfile: data => http.put('user/profile/', data),
        uploadAvatar: data => http.post('user/avatar/', data),
    },
    course: {
        category: () => http.get('course/category/'),
        actualList: params => http.get('course/actual/', { params }),
        detail: id => http.get(`course/actual/${id}/`),
        chapters: courseId =>
            http.get('course/chapter/', { params: { course_id: courseId } }),
        search: params => http.get('course/search/', { params }),
        comments: courseId => http.get(`course/comment/${courseId}/comments/`),
        postComment: (courseId, data) => http.post(`course/comment/${courseId}/comment/`, data),
        deleteComment: id => http.delete(`course/comment/${id}/delete/`),
        replies: commentId => http.get(`course/comment/${commentId}/replies/`),
    },
    cart: {
        add: data => http.post('cart/add/', data),
        list: () => http.get('cart/list/'),
        remove: courseId => http.delete(`cart/remove/${courseId}/`),
        clear: () => http.delete('cart/clear/'),
        checkout: () => http.post('cart/checkout/', {}),
    },
    order: {
        pay: data => http.post('order/pay/', data),
        /** Pass full callback query string, e.g. location.search.slice(1) or empty string */
        successQuery: qs =>
            http.get('order/success/', { params: Object.fromEntries(new URLSearchParams(qs || '')) }),
        list: params => http.get('order/list/', { params }),    // 订单列表（分页+status过滤）
        detail: id => http.get(`order/${id}/`),                 // 订单详情
        cancel: id => http.post(`order/${id}/cancel/`),         // 取消订单
    },
}
