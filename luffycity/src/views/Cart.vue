<template>
    <div class="cart-page">
        <div class="main">
            <div class="page-title">
                <span class="title-bar"></span>
                <h2>我的购物车</h2>
                <span class="count" v-if="!loading">共 {{ cartItems.length }} 门课程</span>
            </div>

            <el-skeleton v-if="loading" :rows="6" animated/>

            <div v-else-if="cartItems.length === 0" class="empty">
                <img src="@/assets/img/cart.svg" alt="">
                <p>购物车还是空的</p>
                <button class="go-course" @click="$router.push('/actual-course')">去选课</button>
            </div>

            <template v-else>
                <ul class="cart-list">
                    <li class="cart-item" v-for="item in cartItems" :key="item.course_id">
                        <router-link :to="`/actual/detail/${item.course_id}`" class="course-link">
                            <img :src="courseImg(item.course_img) || require('@/assets/img/avatar1.svg')" :alt="item.name" loading="lazy">
                            <div class="info">
                                <p class="name">{{ item.name }}</p>
                                <p class="price">¥{{ item.price }}</p>
                            </div>
                        </router-link>
                        <button class="remove-btn" @click="removeItem(item.course_id)">移除</button>
                    </li>
                </ul>

                <div class="cart-footer">
                    <div class="left">
                        <button class="clear-btn" @click="clearCart">清空购物车</button>
                    </div>
                    <div class="right">
                        <p class="total">合计：<span>¥{{ totalAmount }}</span></p>
                        <button class="checkout-btn" @click="checkout">去结算</button>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    import { api } from '@/api'
    import { normalizeMediaSrc } from '@/utils/media'

    export default {
        name: 'Cart',
        data () {
            return {
                loading: true,
                cartItems: [],
            }
        },
        computed: {
            totalAmount () {
                const sum = this.cartItems.reduce((acc, item) => acc + parseFloat(item.price || 0), 0)
                return sum.toFixed(2)
            },
        },
        created () {
            this.fetchCart()
        },
        methods: {
            courseImg (raw) {
                return normalizeMediaSrc(raw)
            },
            fetchCart () {
                this.loading = true
                api.cart.list()
                    .then(res => {
                        if (res.data.status === 100) {
                            this.cartItems = res.data.cart_items || []
                            this.$store.commit('SET_CART_COUNT', res.data.cart_count || 0)
                        } else {
                            this.$message.error(res.data.msg || '获取购物车失败')
                        }
                    })
                    .catch(() => {
                        this.$message.error('获取购物车失败')
                    })
                    .finally(() => {
                        this.loading = false
                    })
            },
            removeItem (courseId) {
                api.cart.remove(courseId)
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('已移除')
                            this.$store.commit('SET_CART_COUNT', res.data.cart_count || 0)
                            this.fetchCart()
                        } else {
                            this.$message.error(res.data.msg || '移除失败')
                        }
                    })
                    .catch(() => {
                        this.$message.error('移除失败')
                    })
            },
            clearCart () {
                this.$confirm('确定清空购物车吗？', '提示', { type: 'warning' })
                    .then(() => api.cart.clear())
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('购物车已清空')
                            this.cartItems = []
                            this.$store.commit('SET_CART_COUNT', 0)
                        } else {
                            this.$message.error(res.data.msg || '清空失败')
                        }
                    })
                    .catch(err => {
                        if (err !== 'cancel') {
                            this.$message.error('清空失败')
                        }
                    })
            },
            checkout () {
                if (!this.$store.getters.isLoggedIn) {
                    this.$message.warning('请先登录后再结算')
                    return
                }
                api.cart.checkout()
                    .then(res => {
                        if (res.data.status === 100 && res.data.pay_url) {
                            open(res.data.pay_url, '_self')
                        } else {
                            this.$message.error(res.data.msg || '结算失败')
                        }
                    })
                    .catch(() => {
                        this.$message.error('结算失败')
                    })
            },
        },
    }
</script>

<style scoped>
    .cart-page {
        background: #f6f6f6;
        min-height: calc(100vh - 200px);
        padding-bottom: 40px;
    }

    .main {
        width: 1200px;
        margin: 0 auto;
        padding-top: 30px;
    }

    .page-title {
        background: #fff;
        padding: 20px 30px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        overflow: hidden;
    }

    .page-title h2 {
        float: left;
        font-size: 20px;
        color: #333;
        font-weight: normal;
        line-height: 24px;
    }

    .title-bar {
        float: left;
        width: 2px;
        height: 20px;
        background: #ffc210;
        margin-right: 12px;
    }

    .page-title .count {
        float: right;
        font-size: 14px;
        color: #9b9b9b;
        line-height: 24px;
    }

    .empty {
        background: #fff;
        text-align: center;
        padding: 80px 0;
        box-shadow: 0 2px 4px 0 #f0f0f0;
    }

    .empty img {
        width: 64px;
        opacity: 0.5;
        margin-bottom: 20px;
    }

    .empty p {
        font-size: 16px;
        color: #9b9b9b;
        margin-bottom: 24px;
    }

    .go-course {
        width: 140px;
        height: 40px;
        border: none;
        background: #ffc210;
        border-radius: 4px;
        color: #fff;
        font-size: 14px;
        cursor: pointer;
    }

    .cart-list {
        background: #fff;
        box-shadow: 0 2px 4px 0 #f0f0f0;
    }

    .cart-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 30px;
        border-bottom: 1px solid #f2f2f2;
    }

    .cart-item:last-child {
        border-bottom: none;
    }

    .course-link {
        display: flex;
        align-items: center;
        flex: 1;
        text-decoration: none;
        color: inherit;
    }

    .course-link img {
        width: 120px;
        height: 68px;
        object-fit: cover;
        border-radius: 4px;
        margin-right: 20px;
    }

    .info .name {
        font-size: 16px;
        color: #333;
        margin-bottom: 10px;
    }

    .info .price {
        font-size: 18px;
        color: #fa6240;
    }

    .remove-btn {
        width: 72px;
        height: 32px;
        border: 1px solid #ddd;
        background: #fff;
        border-radius: 4px;
        color: #666;
        font-size: 13px;
        cursor: pointer;
    }

    .remove-btn:hover {
        color: #fa6240;
        border-color: #fa6240;
    }

    .cart-footer {
        background: #fff;
        margin-top: 20px;
        padding: 20px 30px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        overflow: hidden;
    }

    .cart-footer .left {
        float: left;
    }

    .cart-footer .right {
        float: right;
        text-align: right;
    }

    .clear-btn {
        height: 36px;
        padding: 0 16px;
        border: 1px solid #ddd;
        background: #fff;
        border-radius: 4px;
        color: #666;
        font-size: 14px;
        cursor: pointer;
    }

    .total {
        font-size: 14px;
        color: #666;
        margin-bottom: 12px;
    }

    .total span {
        font-size: 24px;
        color: #fa6240;
    }

    .checkout-btn {
        width: 140px;
        height: 44px;
        border: none;
        background: #ffc210;
        border-radius: 4px;
        color: #fff;
        font-size: 16px;
        cursor: pointer;
    }
</style>
