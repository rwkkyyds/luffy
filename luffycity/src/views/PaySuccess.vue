<template>
    <div class="pay-success">
        <div class="main">
            <div class="title">
                <div class="success-tips">
                    <p v-if="verifying" class="tips">正在同步支付状态…</p>
                    <template v-else-if="paid">
                        <p class="tips">{{ paidMsg }}</p>
                        <p class="tips-sub">感谢您的购买，可前往实战课列表选课学习。</p>
                    </template>
                    <template v-else>
                        <p class="tips">暂未在服务端确认到支付记录</p>
                        <p class="tips-sub">请稍后刷新本页或通过订单渠道核对。</p>
                    </template>
                </div>
            </div>
            <div class="study">
                <span @click="$router.push('/actual-course')">去选课</span>
            </div>
        </div>
    </div>
</template>

<script>
    import { api } from '@/api'

    export default {
        name: 'Success',
        data () {
            return {
                verifying: true,
                paid: false,
                paidMsg: '',
            }
        },
        created () {
            const qs = location.search.startsWith('?')
                ? location.search.slice(1)
                : location.search.replace(/^\?/, '')
            api.order.successQuery(qs)
                .then(response => {
                    if (response.data.status === 100) {
                        this.paid = true
                        this.paidMsg = response.data.msg || '订单支付成功'
                    } else if (response.data.msg) {
                        this.paidMsg = response.data.msg
                    }
                })
                .catch(() => {
                    this.$message.error('支付核对请求失败')
                })
                .finally(() => {
                    this.verifying = false
                })
        },
    }
</script>

<style scoped>
    .main {
        padding: 60px 0;
        margin: 0 auto;
        width: 1200px;
        background: #fff;
        min-height: 400px;
    }

    .main .title {
        display: flex;
        align-items: center;
        padding: 25px 40px;
        border-bottom: 1px solid #f2f2f2;
    }

    .title .tips {
        font-size: 22px;
        color: #000;
        margin-bottom: 8px;
    }

    .tips-sub {
        font-size: 15px;
        color: #9d9d9d;
        margin-top: 0;
    }


    .study {
        padding: 25px 40px;
    }

    .study span {
        display: inline-block;
        width: 140px;
        height: 42px;
        text-align: center;
        line-height: 42px;
        cursor: pointer;
        background: #ffc210;
        border-radius: 6px;
        font-size: 16px;
        color: #fff;
    }
</style>
