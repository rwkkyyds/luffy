<template>
    <div class="profile-page">
        <div class="main">
            <div class="page-title">
                <span class="title-bar"></span>
                <h2>个人中心</h2>
            </div>

            <el-skeleton v-if="loading" :rows="6" animated/>

            <div v-else class="profile-card">
                <div class="avatar-section">
                    <img class="avatar" :src="avatarUrl" alt="">
                    <div class="avatar-actions">
                        <label class="upload-btn">
                            更换头像
                            <input type="file" accept="image/*" @change="onAvatarChange" hidden>
                        </label>
                    </div>
                </div>

                <div class="form-section">
                    <div class="form-row">
                        <span class="label">用户名</span>
                        <el-input v-model="form.username" maxlength="18" show-word-limit/>
                    </div>
                    <div class="form-row">
                        <span class="label">手机号</span>
                        <el-input v-model="form.mobile" maxlength="11" placeholder="请输入手机号"/>
                    </div>
                    <div class="form-row">
                        <span class="label">邮箱</span>
                        <el-input v-model="form.email" placeholder="请输入邮箱"/>
                    </div>
                    <div class="form-actions">
                        <button class="save-btn" :disabled="saving" @click="saveProfile">
                            {{ saving ? '保存中...' : '保存修改' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import { api } from '@/api'
    import { normalizeMediaSrc } from '@/utils/media'
    import { mapState } from 'vuex'

    export default {
        name: 'UserProfile',
        data () {
            return {
                loading: true,
                saving: false,
                form: {
                    username: '',
                    mobile: '',
                    email: '',
                },
                avatarUrl: '',
            }
        },
        computed: {
            ...mapState(['username', 'icon']),
        },
        created () {
            this.fetchProfile()
        },
        methods: {
            fetchProfile () {
                this.loading = true
                api.user.profile()
                    .then(res => {
                        if (res.data.status === 100) {
                            const d = res.data.data
                            this.form.username = d.username || ''
                            this.form.mobile = d.mobile || ''
                            this.form.email = d.email || ''
                            this.avatarUrl = normalizeMediaSrc(d.icon) || require('@/assets/img/avatar1.svg')
                        }
                    })
                    .catch(() => {
                        this.$message.error('获取个人信息失败')
                    })
                    .finally(() => {
                        this.loading = false
                    })
            },
            saveProfile () {
                if (!this.form.username.trim()) {
                    this.$message.warning('用户名不能为空')
                    return
                }
                this.saving = true
                api.user.updateProfile({
                    username: this.form.username,
                    mobile: this.form.mobile,
                    email: this.form.email,
                }).then(res => {
                    if (res.data.status === 100) {
                        this.$message.success('保存成功')
                        this.$store.commit('SET_USER', {
                            token: this.$store.state.token,
                            username: this.form.username,
                            icon: this.icon,
                        })
                    } else {
                        this.$message.error(res.data.msg || '保存失败')
                    }
                }).catch(() => {
                    this.$message.error('保存失败')
                }).finally(() => {
                    this.saving = false
                })
            },
            onAvatarChange (e) {
                const file = e.target.files[0]
                if (!file) return
                if (file.size > 2 * 1024 * 1024) {
                    this.$message.warning('头像不能超过 2MB')
                    return
                }
                const fd = new FormData()
                fd.append('icon', file)
                api.user.uploadAvatar(fd)
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('头像上传成功')
                            const newIcon = res.data.icon
                            this.avatarUrl = normalizeMediaSrc(newIcon) || this.avatarUrl
                            this.$store.commit('SET_USER', {
                                token: this.$store.state.token,
                                username: this.username,
                                icon: newIcon,
                            })
                        } else {
                            this.$message.error(res.data.msg || '上传失败')
                        }
                    })
                    .catch(() => {
                        this.$message.error('上传失败')
                    })
                e.target.value = ''
            },
        },
    }
</script>

<style scoped>
    .profile-page {
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

    .profile-card {
        background: #fff;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        padding: 40px;
        display: flex;
        gap: 60px;
    }

    .avatar-section {
        text-align: center;
        flex-shrink: 0;
    }

    .avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 16px;
        border: 2px solid #f0f0f0;
    }

    .upload-btn {
        display: inline-block;
        padding: 6px 16px;
        background: #ffc210;
        color: #fff;
        border-radius: 4px;
        font-size: 13px;
        cursor: pointer;
    }

    .form-section {
        flex: 1;
    }

    .form-row {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }

    .form-row .label {
        width: 70px;
        font-size: 14px;
        color: #666;
        flex-shrink: 0;
    }

    .form-actions {
        padding-left: 70px;
    }

    .save-btn {
        width: 140px;
        height: 40px;
        background: #ffc210;
        color: #fff;
        border: none;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
    }

    .save-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
</style>
