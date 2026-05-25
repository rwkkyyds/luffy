<template>
    <div class="order-page">
        <div class="main">
            <div class="page-title">
                <span class="title-bar"></span>
                <h2>我的订单</h2>
            </div>

            <div class="status-tabs">
                <span :class="{active: statusFilter === ''}" @click="changeStatus('')">全部</span>
                <span :class="{active: statusFilter === '0'}" @click="changeStatus('0')">未支付</span>
                <span :class="{active: statusFilter === '1'}" @click="changeStatus('1')">已支付</span>
                <span :class="{active: statusFilter === '2'}" @click="changeStatus('2')">已取消</span>
            </div>

            <el-skeleton v-if="loading" :rows="6" animated/>

            <div v-else-if="orders.length === 0" class="empty">
                <p>暂无订单</p>
                <button class="go-course" @click="$router.push('/actual-course')">去选课</button>
            </div>

            <template v-else>
                <div class="order-item" v-for="order in orders" :key="order.id">
                    <div class="order-header">
                        <span class="order-no">订单号：{{ order.out_trade_no }}</span>
                        <span class="order-time">{{ formatTime(order.created_time) }}</span>
                        <span class="order-status" :class="'status-' + order.order_status">{{ order.status_name }}</span>
                    </div>
                    <div class="order-body">
                        <div class="course-info" v-for="item in order.courses" :key="item.course">
                            <img :src="courseImg(item.course_img)" :alt="item.course_name" loading="lazy">
                            <span class="course-name">{{ item.course_name }}</span>
                            <span class="course-price">&yen;{{ item.real_price }}</span>
                        </div>
                    </div>
                    <div class="order-footer">
                        <span class="total">合计：<em>&yen;{{ order.total_amount }}</em></span>
                        <div class="actions">
                            <button v-if="order.order_status === 0" class="pay-btn" @click="goPay(order)">去支付</button>
                            <button v-if="order.order_status === 0" class="cancel-btn" @click="cancelOrder(order)">取消订单</button>
                            <router-link v-if="order.order_status === 1" :to="`/pay/success?out_trade_no=${order.out_trade_no}`" class="detail-link">查看支付结果</router-link>
                        </div>
                    </div>
                </div>

                <el-pagination
                    v-if="total > pageSize"
                    layout="prev, pager, next"
                    :total="total"
                    :page-size="pageSize"
                    :current-page="page"
                    @current-change="handlePageChange"
                    style="text-align:center; margin-top:20px;"
                />
            </template>
        </div>
    </div>
</template>

<script>
    // 订单列表页：支持按状态筛选（全部/未支付/已支付/已取消）、分页、取消订单、去支付
    import { api } from '@/api'
    import { normalizeMediaSrc } from '@/utils/media'

    export default {
        name: 'OrderList',
        data () {
            return {
                loading: true,
                orders: [],
                total: 0,
                page: 1,
                pageSize: 10,
                statusFilter: '',  // ''=全部, '0'=未支付, '1'=已支付, '2'=已取消
            }
        },
        created () {
            this.fetchOrders()
        },
        methods: {
            // 拉取订单列表，带分页和可选的状态过滤
            fetchOrders () {
                this.loading = true
                const params = {
                    page: this.page,
                    page_size: this.pageSize,
                }
                if (this.statusFilter !== '') {
                    params.status = this.statusFilter
                }
                api.order.list(params)
                    .then(res => {
                        this.orders = res.data.results || []
                        this.total = res.data.count || 0
                    })
                    .catch(() => {
                        this.$message.error('获取订单列表失败')
                    })
                    .finally(() => {
                        this.loading = false
                    })
            },
            changeStatus (val) {
                this.statusFilter = val
                this.page = 1
                this.fetchOrders()
            },
            handlePageChange (val) {
                this.page = val
                this.fetchOrders()
            },
            // 取消订单：二次确认 → POST /order/<id>/cancel/ → 刷新列表
            cancelOrder (order) {
                this.$confirm('确定取消该订单吗？', '提示', { type: 'warning' })
                    .then(() => api.order.cancel(order.id))
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('订单已取消')
                            this.fetchOrders()
                        } else {
                            this.$message.error(res.data.msg || '取消失败')
                        }
                    })
                    .catch(err => {
                        // err === 'cancel' 表示用户点了取消按钮，不提示错误
                        if (err !== 'cancel') {
                            this.$message.error('取消失败')
                        }
                    })
            },
            // 重新发起支付：用订单信息调用 /order/pay/ 拿到支付宝链接并跳转
            goPay (order) {
                api.order.pay({
                    subject: order.subject,
                    total_amount: order.total_amount,
                    pay_type: order.pay_type,
                    courses: order.courses.map(c => c.course),
                }).then(res => {
                    if (res.data.status === 100 && res.data.pay_url) {
                        open(res.data.pay_url, '_self')
                    } else {
                        this.$message.error(res.data.msg || '获取支付链接失败')
                    }
                }).catch(() => {
                    this.$message.error('获取支付链接失败')
                })
            },
            courseImg (raw) {
                return normalizeMediaSrc(raw) || require('@/assets/img/avatar1.svg')
            },
            formatTime (iso) {
                if (!iso) return ''
                const d = new Date(iso)
                if (Number.isNaN(d.getTime())) return String(iso)
                const pad = n => String(n).padStart(2, '0')
                return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
            },
        },
    }
</script>

<style scoped>
    .order-page {
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

    .status-tabs {
        background: #fff;
        padding: 16px 30px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
    }

    .status-tabs span {
        display: inline-block;
        padding: 6px 20px;
        margin-right: 10px;
        cursor: pointer;
        font-size: 14px;
        color: #666;
        border-radius: 4px;
        transition: all .2s;
    }

    .status-tabs span:hover {
        color: #ffc210;
    }

    .status-tabs span.active {
        background: #ffc210;
        color: #fff;
    }

    .empty {
        background: #fff;
        text-align: center;
        padding: 80px 0;
        box-shadow: 0 2px 4px 0 #f0f0f0;
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

    .order-item {
        background: #fff;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        border-radius: 4px;
        overflow: hidden;
    }

    .order-header {
        display: flex;
        align-items: center;
        padding: 14px 24px;
        background: #fafafa;
        border-bottom: 1px solid #f0f0f0;
        font-size: 13px;
        color: #999;
    }

    .order-no {
        margin-right: 24px;
    }

    .order-time {
        flex: 1;
    }

    .order-status {
        font-weight: 500;
    }

    .status-0 { color: #fa6240; }
    .status-1 { color: #67c23a; }
    .status-2 { color: #999; }
    .status-3 { color: #999; }

    .order-body {
        padding: 16px 24px;
    }

    .course-info {
        display: flex;
        align-items: center;
        padding: 8px 0;
    }

    .course-info img {
        width: 80px;
        height: 45px;
        object-fit: cover;
        border-radius: 4px;
        margin-right: 14px;
    }

    .course-name {
        flex: 1;
        font-size: 14px;
        color: #333;
    }

    .course-price {
        font-size: 14px;
        color: #666;
    }

    .order-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 24px;
        border-top: 1px solid #f0f0f0;
    }

    .total {
        font-size: 14px;
        color: #666;
    }

    .total em {
        font-style: normal;
        font-size: 18px;
        color: #fa6240;
        font-weight: 500;
    }

    .actions button,
    .actions .detail-link {
        margin-left: 12px;
        height: 32px;
        padding: 0 16px;
        border-radius: 4px;
        font-size: 13px;
        cursor: pointer;
        border: none;
        display: inline-flex;
        align-items: center;
        text-decoration: none;
    }

    .pay-btn {
        background: #ffc210;
        color: #fff;
    }

    .cancel-btn {
        background: #fff;
        color: #666;
        border: 1px solid #ddd !important;
    }

    .detail-link {
        color: #ffc210;
        border: 1px solid #ffc210 !important;
        background: #fff;
    }
</style>
