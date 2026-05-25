<template>
    <div class="register">
        <div class="box">
            <i class="el-icon-close" @click="close_register"></i>
            <div class="content">
                <div class="nav">
                    <span class="active">新用户注册</span>
                </div>
                <el-form>
                    <el-input
                            placeholder="手机号"
                            prefix-icon="el-icon-phone-outline"
                            v-model="mobile"
                            clearable
                            @blur="check_mobile">
                    </el-input>
                    <el-input
                            placeholder="密码"
                            prefix-icon="el-icon-key"
                            v-model="password"
                            clearable
                            show-password>
                    </el-input>
                    <el-input
                            placeholder="验证码"
                            prefix-icon="el-icon-chat-line-round"
                            v-model="sms"
                            clearable>
                        <template slot="append">
                            <span class="sms" @click="send_sms">{{ sms_interval }}</span>
                        </template>
                    </el-input>
                    <el-button type="primary" @click="handleRegister">注册</el-button>
                </el-form>
                <div class="foot">
                    <span @click="go_login">立即登录</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import { sendSmsMixin } from '@/mixins/sendSmsMixin'
    import { parseErrorMsg } from '@/utils/media'

    export default {
        name: "Register",
        mixins: [sendSmsMixin],
        data () {
            return {
                mobile: '',
                password: '',
                sms: '',
            }
        },
        methods: {
            close_register() {
                this.$emit('close', false)
            },
            go_login() {
                this.$emit('go')
            },
            check_mobile() {
                if (!this.mobile) return;
                if (!this.mobile.match(/^1[3-9][0-9]{9}$/)) {
                    this.$message({
                        message: '手机号有误',
                        type: 'warning',
                        duration: 1000,
                        onClose: () => {
                            this.mobile = '';
                        }
                    });
                    return false;
                }
                // 加一个校验手机号是否存在的功能
                this.is_send = true;
            },
            send_sms () {
                if (!this.is_send) return
                this.startSmsCooldown()
                // 发送短信 验证码
                this.$axios.get('user/send/send_message/?phone=' + this.mobile).then(res => {
                    if (res.data.status == 100) {
                        this.$message({
                            message: '恭喜你，验证码发送成功',
                            type: 'success'
                        });
                    } else {
                        this.$message({
                            message: '验证码发送失败，请稍后再试',
                            type: 'warning'
                        });
                    }
                })

            },
            handleRegister(){
                 if (this.mobile && this.sms && this.password) {
                    this.$axios.post(
                        'user/register/',
                        {
                            mobile: this.mobile,
                            code: this.sms,
                            password:this.password
                        }).then(res => {
                        if (res.data.status == 100) {
                            if (process.env.NODE_ENV === 'development') {
                                // eslint-disable-next-line no-console
                                console.log('[register]', res.data)
                            }
                            this.$message('恭喜您，注册成功');
                            //2 关闭注册框
                            this.close_register()
                        } else {
                            this.$message.error(parseErrorMsg(res.data.msg));
                        }
                    })

                } else {
                    this.$message.error('用户名密码必填');
                }
            }
        }
    }
</script>

<style scoped>
    .register {
        width: 100vw;
        height: 100vh;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 10;
        background-color: rgba(0, 0, 0, 0.3);
    }

    .box {
        width: 400px;
        height: 480px;
        background-color: white;
        border-radius: 10px;
        position: relative;
        top: calc(50vh - 240px);
        left: calc(50vw - 200px);
    }

    .el-icon-close {
        position: absolute;
        font-weight: bold;
        font-size: 20px;
        top: 10px;
        right: 10px;
        cursor: pointer;
    }

    .el-icon-close:hover {
        color: darkred;
    }

    .content {
        position: absolute;
        top: 40px;
        width: 280px;
        left: 60px;
    }

    .nav {
        font-size: 20px;
        height: 38px;
        border-bottom: 2px solid darkgrey;
    }

    .nav > span {
        margin-left: 90px;
        color: darkgrey;
        user-select: none;
        cursor: pointer;
        padding-bottom: 10px;
        border-bottom: 2px solid darkgrey;
    }

    .nav > span.active {
        color: black;
        border-bottom: 3px solid black;
        padding-bottom: 9px;
    }

    .el-input, .el-button {
        margin-top: 40px;
    }

    .el-button {
        width: 100%;
        font-size: 18px;
    }

    .foot > span {
        float: right;
        margin-top: 20px;
        color: orange;
        cursor: pointer;
    }

    .sms {
        color: orange;
        cursor: pointer;
        display: inline-block;
        width: 70px;
        text-align: center;
        user-select: none;
    }
</style>