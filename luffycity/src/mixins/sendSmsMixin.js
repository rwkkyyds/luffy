/** 登录 / 注册共用的验证码倒计时 UI 状态（方案 A：减少重复代码） */
export const sendSmsMixin = {
    data () {
        return {
            sms_interval: '获取验证码',
            is_send: false,
        }
    },
    methods: {
        startSmsCooldown () {
            this.is_send = false
            let countdown = 60
            this.sms_interval = '发送中…'
            const timer = setInterval(() => {
                if (countdown <= 1) {
                    clearInterval(timer)
                    this.sms_interval = '获取验证码'
                    this.is_send = true
                } else {
                    countdown -= 1
                    this.sms_interval = `${countdown}秒后再发`
                }
            }, 1000)
        },
    },
}
