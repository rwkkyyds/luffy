import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
    { path: '/', redirect: '/home' },
    {
        path: '/home',
        name: 'home',
        component: () => import(/* webpackChunkName: "home" */ '../views/HomeView.vue'),
    },
    {
        path: '/login',
        name: 'login',
        component: () => import(/* webpackChunkName: "auth" */ '../components/Login.vue'),
    },
    {
        path: '/actual-course',
        name: 'ActualCourse',
        component: () => import(/* webpackChunkName: "course" */ '../views/ActualCourse.vue'),
    },
    {
        path: '/free-course',
        name: 'FreeCourse',
        component: () => import(/* webpackChunkName: "course-free" */ '../views/FreeCourse.vue'),
    },
    {
        path: '/light-course',
        name: 'LightCourse',
        component: () => import(/* webpackChunkName: "course-light" */ '../views/LightCourse.vue'),
    },
    {
        path: '/actual/detail/:pk',
        name: 'CourseDetail',
        component: () => import(/* webpackChunkName: "course-detail" */ '../views/CourseDetail.vue'),
    },
    {
        path: '/course/search',
        name: 'SearchCourse',
        component: () => import(/* webpackChunkName: "search" */ '../views/SearchCourse.vue'),
    },
    {
        path: '/cart',
        name: 'Cart',
        component: () => import(/* webpackChunkName: "cart" */ '../views/Cart.vue'),
    },
    {
        path: '/pay/success',
        name: 'pay-success',
        component: () => import(/* webpackChunkName: "pay" */ '../views/PaySuccess.vue'),
    },
    {   // 我的订单列表页（新增）
        path: '/orders',
        name: 'OrderList',
        component: () => import(/* webpackChunkName: "order" */ '../views/OrderList.vue'),
    },
    {
        path: '/ai-chat',
        name: 'AiChat',
        component: () => import(/* webpackChunkName: "ai" */ '../views/AiChat.vue'),
    },
    {
        path: '/profile',
        name: 'UserProfile',
        component: () => import(/* webpackChunkName: "profile" */ '../views/UserProfile.vue'),
    },
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
})

export default router
