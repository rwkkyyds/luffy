<template>
    <div class="detail">
        <div class="main">
            <el-skeleton v-if="course_loading" :rows="10" animated/>
            <template v-else>
            <div class="course-info">
                <div class="wrap-left">
                    <vue-core-video-player :src="mp4_url"
                                           controls="auto"
                                           autoplay
                                           :muted="true"
                                           title="致命诱惑"
                                           @play="playFunc"
                                           @pause="pauseFunc"
                    ></vue-core-video-player>
                </div>
                <div class="wrap-right">
                    <h3 class="course-name">{{course_info.name}}</h3>
                    <p class="data">{{course_info.students}}人在学&nbsp;&nbsp;&nbsp;&nbsp;课程总时长：{{course_info.sections}}课时/{{course_info.pub_sections}}小时&nbsp;&nbsp;&nbsp;&nbsp;难度：{{course_info.level_name}}</p>
                    <div class="sale-time">
                        <p class="sale-type">价格 <span class="original_price">¥{{course_info.price}}</span></p>
                        <p class="expire"></p>
                    </div>
                    <div class="buy">
                        <div class="buy-btn">
                            <button class="buy-now" @click="go_pay(course_info)">立即购买</button>
                            <button class="free">免费试学</button>
                        </div>
                        <div class="add-cart" @click="add_cart(course_info.id)">
                            <img src="@/assets/img/cart-yellow.svg" alt="">加入购物车
                        </div>
                    </div>
                </div>
            </div>
            <div class="course-tab">
                <ul class="tab-list">
                    <li :class="tabIndex==1?'active':''" @click="tabIndex=1">详情介绍</li>
                    <li :class="tabIndex==2?'active':''" @click="tabIndex=2">课程章节 <span :class="tabIndex!=2?'free':''">(试学)</span>
                    </li>
                    <li :class="tabIndex==3?'active':''" @click="tabIndex=3">用户评论</li>
                    <li :class="tabIndex==4?'active':''" @click="tabIndex=4">常见问题</li>
                </ul>
            </div>
            <div class="course-content">
                <div class="course-tab-list">
                    <div class="tab-item" v-if="tabIndex==1">
                        <div class="course-brief" v-html="sanitizedBrief"></div>
                    </div>
                    <div class="tab-item" v-if="tabIndex==2">
                        <div class="tab-item-title">
                            <p class="chapter">课程章节</p>
                            <p class="chapter-length">共{{course_chapters.length}}章 {{course_info.sections}}个课时</p>
                        </div>
                        <div class="chapter-item" v-for="chapter in course_chapters" :key="chapter.name">
                            <p class="chapter-title"><img src="@/assets/img/enum.svg" alt="">第{{chapter.chapter}}章·{{chapter.name}}
                            </p>
                            <ul class="section-list">
                                <li class="section-item" v-for="section in chapter.coursesections" :key="section.name">
                                    <p class="name"><span class="index">{{chapter.chapter}}-{{section.orders}}</span>
                                        {{section.name}}<span class="free" v-if="section.free_trail">免费</span></p>
                                    <p class="time">{{section.duration}} <img src="@/assets/img/chapter-player.svg"></p>
                                    <button class="try" v-if="section.free_trail">立即试学</button>
                                    <button class="try" v-else>立即购买</button>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div class="tab-item comment-panel" v-if="tabIndex==3">
                        <div class="comment-form" v-if="isLoggedIn">
                            <p class="form-title">{{ replyTarget ? '回复 @' + replyTarget.username : '发表评论' }}</p>
                            <div class="form-row">
                                <span class="label">评分</span>
                                <el-rate v-model="commentForm.score" :colors="['#ffc210', '#ffc210', '#ffc210']"/>
                            </div>
                            <el-input
                                type="textarea"
                                :rows="4"
                                maxlength="500"
                                show-word-limit
                                :placeholder="replyTarget ? '写下你的回复（10-500字）' : '写下你对这门课程的评价（10-500字）'"
                                v-model="commentForm.content"
                                @keydown.enter.native.ctrl="submitComment"
                            />
                            <div class="form-actions">
                                <button v-if="replyTarget" class="cancel-btn" @click="cancelReply">取消回复</button>
                                <button class="submit-btn" :disabled="commentSubmitting" @click="submitComment">
                                    {{ replyTarget ? '提交回复' : '发表评论' }}
                                </button>
                            </div>
                        </div>
                        <div v-else class="comment-login-tip">
                            <p>登录后即可发表评论</p>
                            <span @click="openLogin">立即登录</span>
                        </div>

                        <el-skeleton v-if="comments_loading" :rows="4" animated style="margin-top: 20px"/>
                        <div v-else-if="comments.length === 0" class="comment-empty">暂无评论，快来抢沙发吧~</div>
                        <ul v-else class="comment-list">
                            <li class="comment-item" v-for="comment in comments" :key="comment.id">
                                <img class="avatar" :src="userIcon(comment.icon)" alt="">
                                <div class="body">
                                    <div class="meta">
                                        <span class="username">{{ comment.username }}</span>
                                        <el-rate :value="comment.score" disabled :colors="['#ffc210', '#ffc210', '#ffc210']"/>
                                        <span class="time">{{ formatTime(comment.created_time) }}</span>
                                    </div>
                                    <p class="content">{{ comment.content }}</p>
                                    <div class="actions">
                                        <span @click="startReply(comment)" v-if="isLoggedIn">回复</span>
                                        <span v-if="canDelete(comment)" class="delete" @click="deleteComment(comment.id)">删除</span>
                                    </div>
                                    <!-- 递归渲染回复树 -->
                                    <div class="reply-section" v-if="comment.replies && comment.replies.length">
                                        <div v-if="replyVisibleCount[comment.id] > 0">
                                            <ul class="reply-list">
                                                <template v-for="reply in visibleReplies(comment)">
                                                    <li :key="reply.id" class="reply-item">
                                                        <img class="avatar small" :src="userIcon(reply.icon)" alt="">
                                                        <div class="body">
                                                            <div class="meta">
                                                                <span class="username">{{ reply.username }}</span>
                                                                <span v-if="reply.parent_username && reply.parent_username !== reply.username" class="reply-to">回复 @{{ reply.parent_username }}</span>
                                                                <span class="time">{{ formatTime(reply.created_time) }}</span>
                                                            </div>
                                                            <p class="content">{{ reply.content }}</p>
                                                            <div class="actions">
                                                                <span @click="startReply(reply)" v-if="isLoggedIn">回复</span>
                                                                <span v-if="canDelete(reply)" class="delete" @click="deleteComment(reply.id)">删除</span>
                                                            </div>
                                                            <!-- 递归渲染子回复 -->
                                                            <div v-if="reply.replies && reply.replies.length" class="sub-replies">
                                                                <ul class="reply-list">
                                                                    <li class="reply-item" v-for="sub in reply.replies" :key="sub.id">
                                                                        <img class="avatar small" :src="userIcon(sub.icon)" alt="">
                                                                        <div class="body">
                                                                            <div class="meta">
                                                                                <span class="username">{{ sub.username }}</span>
                                                                                <span v-if="sub.parent_username && sub.parent_username !== sub.username" class="reply-to">回复 @{{ sub.parent_username }}</span>
                                                                                <span class="time">{{ formatTime(sub.created_time) }}</span>
                                                                            </div>
                                                                            <p class="content">{{ sub.content }}</p>
                                                                            <div class="actions">
                                                                                <span @click="startReply(sub)" v-if="isLoggedIn">回复</span>
                                                                                <span v-if="canDelete(sub)" class="delete" @click="deleteComment(sub.id)">删除</span>
                                                                            </div>
                                                                        </div>
                                                                    </li>
                                                                </ul>
                                                            </div>
                                                        </div>
                                                    </li>
                                                </template>
                                            </ul>
                                        </div>
                                        <div class="reply-actions">
                                            <span v-if="replyVisibleCount[comment.id] === 0" @click="expandReplies(comment)">
                                                展开{{ comment.replies.length }}条回复
                                            </span>
                                            <span v-else-if="hasMoreReplies(comment)" @click="loadMoreReplies(comment)">
                                                展开更多
                                            </span>
                                            <span v-if="replyVisibleCount[comment.id] > 0" class="collapse" @click="collapseReplies(comment)">
                                                收起回复
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div class="tab-item" v-if="tabIndex==4">
                        <el-alert title="常见问题功能开发中" type="info" show-icon :closable="false"/>
                    </div>
                </div>
                <div class="course-side">
                    <div class="teacher-info">
                        <h4 class="side-title"><span>授课老师</span></h4>
                        <div class="teacher-content">
                            <div class="cont1">
                                <img :src="course_info.teacher.image" loading="lazy" alt="">
                                <div class="name">
                                    <p class="teacher-name">{{course_info.teacher.name}}
                                        {{course_info.teacher.title}}</p>
                                    <p class="teacher-title">{{course_info.teacher.signature}}</p>
                                </div>
                            </div>
                            <p class="narrative">{{course_info.teacher.brief}}</p>
                        </div>
                    </div>
                </div>
            </div>
            </template>
        </div>
    </div>
</template>

<script>
    import DOMPurify from 'dompurify'
    import { api } from '@/api'
    import { mapGetters, mapState } from 'vuex'
    import { normalizeMediaSrc } from '@/utils/media'

    export default {
        name: "Detail",
        computed: {
            ...mapGetters(['isLoggedIn']),
            ...mapState(['username']),
            sanitizedBrief () {
                const html = this.course_info && this.course_info.brief
                return html ? DOMPurify.sanitize(String(html)) : ''
            },
        },
        data() {
            return {
                course_loading: true,
                tabIndex: 2,   // 当前选项卡显示的下标
                course_id: 0, // 当前课程信息的ID
                course_info: {
                    teacher: {},
                }, // 课程信息
                course_chapters: [], // 课程的章节课时列表
                comments: [],
                comments_loading: false,
                commentSubmitting: false,
                commentForm: {
                    content: '',
                    score: 5,
                },
                replyTarget: null,
                replyTopParent: null,
                replyVisibleCount: {},   // { [commentId]: 当前显示的回复数，0=未展开 }
                replyTotal: {},          // { [commentId]: 该评论的回复总数 }
                allReplies: {},          // { [commentId]: 已加载的全部回复数据 }
                repliesLoading: {},      // { [commentId]: 是否正在加载更多 }
                REPLY_BATCH: 3,          // 每次展开的回复数
                // mp4_url:'http://img.ksbbs.com/asset/Mon_1703/05cacb4e02f9d9e.mp4',
                mp4_url:"",
            }
        },
        watch: {
            tabIndex (val) {
                if (val === 3 && !this.comments_loading && this.comments.length === 0) {
                    this.fetchComments()
                }
            },
        },
        created() {
            this.get_course_id();
            this.get_course_data();
            this.get_chapter();
        },
        methods: {
            go_pay (course_info) {
                let token = this.$store.state.token || this.$cookies.get("token")
                if (token) {
                    api.order.pay({
                        "subject": course_info.name,
                        "total_amount": course_info.price,
                        "pay_type": 1,
                        "courses": [course_info.id]
                    }).then(res => {
                        if (res.data.status === 100) {
                            let pay_url = res.data.pay_url
                            // 跳转,在当前窗口打开这个链接
                            open(pay_url, '_self');
                        } else {
                            this.$message({
                                message: "下单失败，请联系统管理员"
                            });
                        }

                    })
                } else {
                    this.$message({
                        message: "对不起，您没有登录，请登陆后购买！"
                    });
                }
            },
            add_cart (courseId) {
                if (!this.course_info || !this.course_info.price) {
                    this.$message.warning('课程信息加载中，请稍后再试')
                    return
                }
                api.cart.add({
                    course_id: Number(courseId),
                    price: this.course_info.price,
                }).then(res => {
                    if (res.data.status === 100) {
                        this.$message.success('已加入购物车')
                        this.$store.commit('SET_CART_COUNT', res.data.cart_count || 0)
                    } else {
                        this.$message.error(res.data.msg || '加入购物车失败')
                    }
                }).catch(() => {
                    this.$message.error('加入购物车失败')
                })
            },
            openLogin () {
                this.$root.$emit('header-open-login')
            },
            fetchComments () {
                this.comments_loading = true
                this.replyVisibleCount = {}
                this.replyTotal = {}
                this.allReplies = {}
                api.course.comments(this.course_id)
                    .then(res => {
                        if (res.data.status === 100) {
                            this.comments = res.data.data || []
                        } else {
                            this.$message.error(res.data.msg || '获取评论失败')
                        }
                    })
                    .catch(() => {
                        this.$message.error('获取评论失败')
                    })
                    .finally(() => {
                        this.comments_loading = false
                    })
            },
            submitComment () {
                const content = (this.commentForm.content || '').trim()
                if (content.length < 10) {
                    this.$message.warning('评论内容至少 10 个字')
                    return
                }
                this.commentSubmitting = true
                const payload = {
                    content,
                    score: this.commentForm.score,
                }
                if (this.replyTarget) {
                    payload.parent_id = this.replyTopParent
                }
                api.course.postComment(this.course_id, payload)
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('评论成功')
                            this.commentForm.content = ''
                            this.commentForm.score = 5
                            this.replyTarget = null
                            this.fetchComments()
                        } else {
                            this.$message.error(res.data.msg || '评论失败')
                        }
                    })
                    .catch(err => {
                        const msg = err.response?.data?.msg
                        this.$message.error(msg || '评论失败')
                    })
                    .finally(() => {
                        this.commentSubmitting = false
                    })
            },
            startReply (comment) {
                this.replyTarget = comment
                this.replyTopParent = comment.id
                this.commentForm.content = ''
            },
            cancelReply () {
                this.replyTarget = null
                this.replyTopParent = null
            },
            visibleReplies (comment) {
                const count = this.replyVisibleCount[comment.id] || 0
                const all = this.allReplies[comment.id] || comment.replies || []
                return all.slice(0, count)
            },
            expandReplies (comment) {
                this.$set(this.replyVisibleCount, comment.id, this.REPLY_BATCH)
                if (!this.allReplies[comment.id]) {
                    this.$set(this.allReplies, comment.id, comment.replies || [])
                    this.$set(this.replyTotal, comment.id, (comment.replies || []).length)
                }
            },
            loadMoreReplies (comment) {
                const loaded = (this.allReplies[comment.id] || []).length
                const current = this.replyVisibleCount[comment.id] || 0
                if (current < loaded) {
                    this.$set(this.replyVisibleCount, comment.id, Math.min(current + this.REPLY_BATCH, loaded))
                    return
                }
                if (this.repliesLoading[comment.id]) return
                this.$set(this.repliesLoading, comment.id, true)
                api.course.replies(comment.id)
                    .then(res => {
                        if (res.data.status === 100) {
                            const all = res.data.data || []
                            this.$set(this.allReplies, comment.id, all)
                            this.$set(this.replyTotal, comment.id, all.length)
                            this.$set(this.replyVisibleCount, comment.id, Math.min(current + this.REPLY_BATCH, all.length))
                        }
                    })
                    .finally(() => {
                        this.$set(this.repliesLoading, comment.id, false)
                    })
            },
            collapseReplies (comment) {
                this.$set(this.replyVisibleCount, comment.id, 0)
            },
            hasMoreReplies (comment) {
                const loaded = (this.allReplies[comment.id] || comment.replies || []).length
                const shown = this.replyVisibleCount[comment.id] || 0
                return shown < loaded
            },
            deleteComment (commentId) {
                this.$confirm('确定删除这条评论吗？', '提示', { type: 'warning' })
                    .then(() => api.course.deleteComment(commentId))
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$message.success('删除成功')
                            this.fetchComments()
                        } else {
                            this.$message.error(res.data.msg || '删除失败')
                        }
                    })
                    .catch(err => {
                        if (err !== 'cancel') {
                            this.$message.error('删除失败')
                        }
                    })
            },
            canDelete (comment) {
                return this.isLoggedIn && comment.username === this.username
            },
            userIcon (raw) {
                const src = normalizeMediaSrc(raw)
                return src || require('@/assets/img/avatar1.svg')
            },
            formatTime (iso) {
                if (!iso) return ''
                const d = new Date(iso)
                if (Number.isNaN(d.getTime())) return String(iso)
                const pad = n => String(n).padStart(2, '0')
                return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
            },
            playFunc () {
                if (process.env.NODE_ENV === 'development') {
                    // eslint-disable-next-line no-console
                    console.log('开始了')
                }
            },
            pauseFunc () {
                if (process.env.NODE_ENV === 'development') {
                    // eslint-disable-next-line no-console
                    console.log('暂停了')
                }
            },
            get_course_id() {
                // 获取地址栏上面的课程ID
                this.course_id = this.$route.params.pk
                if (this.course_id < 1) {
                    let _this = this;
                    _this.$alert("对不起，当前视频不存在！", "警告", {
                        callback() {
                            _this.$router.go(-1);
                        }
                    });
                }
            },
            get_course_data () {
                this.course_loading = true
                api.course.detail(this.course_id).then(response => {
                    this.course_info = response.data;
                    if (process.env.NODE_ENV === 'development') {
                        // eslint-disable-next-line no-console
                        console.log(this.course_info)
                    }
                }).catch(() => {
                    this.$message({
                        message: "对不起，访问页面出错！请联系客服工作人员！"
                    });
                }).finally(() => {
                    this.course_loading = false
                })
            },

            get_chapter () {
                api.course.chapters(this.course_id).then(response => {
                    this.course_chapters = response.data;
                }).catch(error => {
                    if (process.env.NODE_ENV === 'development') {
                        // eslint-disable-next-line no-console
                        console.warn(error.response);
                    }
                })
            },
        },
    }
</script>

<style scoped>
    .main {
        background: #fff;
        padding-top: 30px;
    }

    .course-info {
        width: 1200px;
        margin: 0 auto;
        overflow: hidden;
    }

    .wrap-left {
        float: left;
        width: 690px;
        height: 388px;
        background-color: #000;
    }

    .wrap-right {
        float: left;
        position: relative;
        height: 388px;
    }

    .course-name {
        font-size: 20px;
        color: #333;
        padding: 10px 23px;
        letter-spacing: .45px;
    }

    .data {
        padding-left: 23px;
        padding-right: 23px;
        padding-bottom: 16px;
        font-size: 14px;
        color: #9b9b9b;
    }

    .sale-time {
        width: 464px;
        background: #fa6240;
        font-size: 14px;
        color: #4a4a4a;
        padding: 10px 23px;
        overflow: hidden;
    }

    .sale-type {
        font-size: 16px;
        color: #fff;
        letter-spacing: .36px;
        float: left;
    }

    .sale-time .expire {
        font-size: 14px;
        color: #fff;
        float: right;
    }

    .sale-time .expire .second {
        width: 24px;
        display: inline-block;
        background: #fafafa;
        color: #5e5e5e;
        padding: 6px 0;
        text-align: center;
    }

    .course-price {
        background: #fff;
        font-size: 14px;
        color: #4a4a4a;
        padding: 5px 23px;
    }

    .discount {
        font-size: 26px;
        color: #fa6240;
        margin-left: 10px;
        display: inline-block;
        margin-bottom: -5px;
    }

    .original {
        font-size: 14px;
        color: #9b9b9b;
        margin-left: 10px;
        text-decoration: line-through;
    }

    .buy {
        width: 464px;
        padding: 0px 23px;
        position: absolute;
        left: 0;
        bottom: 20px;
        overflow: hidden;
    }

    .buy .buy-btn {
        float: left;
    }

    .buy .buy-now {
        width: 125px;
        height: 40px;
        border: 0;
        background: #ffc210;
        border-radius: 4px;
        color: #fff;
        cursor: pointer;
        margin-right: 15px;
        outline: none;
    }

    .buy .free {
        width: 125px;
        height: 40px;
        border-radius: 4px;
        cursor: pointer;
        margin-right: 15px;
        background: #fff;
        color: #ffc210;
        border: 1px solid #ffc210;
    }

    .add-cart {
        float: right;
        font-size: 14px;
        color: #ffc210;
        text-align: center;
        cursor: pointer;
        margin-top: 10px;
    }

    .add-cart img {
        width: 20px;
        height: 18px;
        margin-right: 7px;
        vertical-align: middle;
    }

    .course-tab {
        width: 100%;
        background: #fff;
        margin-bottom: 30px;
        box-shadow: 0 2px 4px 0 #f0f0f0;

    }

    .course-tab .tab-list {
        width: 1200px;
        margin: auto;
        color: #4a4a4a;
        overflow: hidden;
    }

    .tab-list li {
        float: left;
        margin-right: 15px;
        padding: 26px 20px 16px;
        font-size: 17px;
        cursor: pointer;
    }

    .tab-list .active {
        color: #ffc210;
        border-bottom: 2px solid #ffc210;
    }

    .tab-list .free {
        color: #fb7c55;
    }

    .course-content {
        width: 1200px;
        margin: 0 auto;
        background: #FAFAFA;
        overflow: hidden;
        padding-bottom: 40px;
    }

    .course-tab-list {
        width: 880px;
        height: auto;
        padding: 20px;
        background: #fff;
        float: left;
        box-sizing: border-box;
        overflow: hidden;
        position: relative;
        box-shadow: 0 2px 4px 0 #f0f0f0;
    }

    .tab-item {
        background: #fff;
        padding-bottom: 20px;
    }

    .tab-item-title {
        justify-content: space-between;
        padding: 25px 20px 11px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-bottom: 1px solid #333;
        border-bottom-color: rgba(51, 51, 51, .05);
        overflow: hidden;
    }

    .chapter {
        font-size: 17px;
        color: #4a4a4a;
        float: left;
    }

    .chapter-length {
        float: right;
        font-size: 14px;
        color: #9b9b9b;
        letter-spacing: .19px;
    }

    .chapter-title {
        font-size: 16px;
        color: #4a4a4a;
        letter-spacing: .26px;
        padding: 12px;
        background: #eee;
        border-radius: 2px;
        display: -ms-flexbox;
        display: flex;
        -ms-flex-align: center;
        align-items: center;
    }

    .chapter-title img {
        width: 18px;
        height: 18px;
        margin-right: 7px;
        vertical-align: middle;
    }

    .section-list {
        padding: 0 20px;
    }

    .section-list .section-item {
        padding: 15px 20px 15px 36px;
        cursor: pointer;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }

    .section-item .name {
        font-size: 14px;
        color: #666;
        float: left;
    }

    .section-item .index {
        margin-right: 5px;
    }

    .section-item .free {
        font-size: 12px;
        color: #fff;
        letter-spacing: .19px;
        background: #ffc210;
        border-radius: 100px;
        padding: 1px 9px;
        margin-left: 10px;
    }

    .section-item .time {
        font-size: 14px;
        color: #666;
        letter-spacing: .23px;
        opacity: 1;
        transition: all .15s ease-in-out;
        float: right;
    }

    .section-item .time img {
        width: 18px;
        height: 18px;
        margin-left: 15px;
        vertical-align: text-bottom;
    }

    .section-item .try {
        width: 86px;
        height: 28px;
        background: #ffc210;
        border-radius: 4px;
        font-size: 14px;
        color: #fff;
        position: absolute;
        right: 20px;
        top: 10px;
        opacity: 0;
        transition: all .2s ease-in-out;
        cursor: pointer;
        outline: none;
        border: none;
    }

    .section-item:hover {
        background: #fcf7ef;
        box-shadow: 0 0 0 0 #f3f3f3;
    }

    .section-item:hover .name {
        color: #333;
    }

    .section-item:hover .try {
        opacity: 1;
    }

    .course-side {
        width: 300px;
        height: auto;
        margin-left: 20px;
        float: right;
    }

    .teacher-info {
        background: #fff;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
    }

    .side-title {
        font-weight: normal;
        font-size: 17px;
        color: #4a4a4a;
        padding: 18px 14px;
        border-bottom: 1px solid #333;
        border-bottom-color: rgba(51, 51, 51, .05);
    }

    .side-title span {
        display: inline-block;
        border-left: 2px solid #ffc210;
        padding-left: 12px;
    }

    .teacher-content {
        padding: 30px 20px;
        box-sizing: border-box;
    }

    .teacher-content .cont1 {
        margin-bottom: 12px;
        overflow: hidden;
    }

    .teacher-content .cont1 img {
        width: 54px;
        height: 54px;
        margin-right: 12px;
        float: left;
    }

    .teacher-content .cont1 .name {
        float: right;
    }

    .teacher-content .cont1 .teacher-name {
        width: 188px;
        font-size: 16px;
        color: #4a4a4a;
        padding-bottom: 4px;
    }

    .teacher-content .cont1 .teacher-title {
        width: 188px;
        font-size: 13px;
        color: #9b9b9b;
        white-space: nowrap;
    }

    .teacher-content .narrative {
        font-size: 14px;
        color: #666;
        line-height: 24px;
    }

    .comment-panel {
        padding: 0 10px 10px;
    }

    .comment-form {
        padding: 20px;
        margin-bottom: 24px;
        background: #fcf7ef;
        border-radius: 4px;
    }

    .form-title {
        font-size: 16px;
        color: #333;
        margin-bottom: 16px;
    }

    .form-row {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }

    .form-row .label {
        font-size: 14px;
        color: #666;
        margin-right: 12px;
    }

    .form-actions {
        margin-top: 16px;
        text-align: right;
    }

    .submit-btn,
    .cancel-btn {
        height: 36px;
        padding: 0 20px;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
        border: none;
    }

    .submit-btn {
        background: #ffc210;
        color: #fff;
    }

    .submit-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .cancel-btn {
        background: #fff;
        color: #666;
        border: 1px solid #ddd;
        margin-right: 12px;
    }

    .comment-login-tip {
        text-align: center;
        padding: 30px 0;
        color: #9b9b9b;
    }

    .comment-login-tip span {
        color: #ffc210;
        cursor: pointer;
        margin-left: 8px;
    }

    .comment-empty {
        text-align: center;
        padding: 40px 0;
        color: #9b9b9b;
        font-size: 14px;
    }

    .comment-list {
        padding: 0;
    }

    .comment-item {
        display: flex;
        padding: 20px 10px;
        border-bottom: 1px solid #f2f2f2;
    }

    .comment-item:last-child {
        border-bottom: none;
    }

    .avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 14px;
        flex-shrink: 0;
    }

    .avatar.small {
        width: 32px;
        height: 32px;
    }

    .comment-item .body {
        flex: 1;
        min-width: 0;
    }

    .meta {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 8px;
    }

    .meta .username {
        font-size: 14px;
        color: #333;
        margin-right: 12px;
    }

    .meta .time {
        font-size: 12px;
        color: #9b9b9b;
        margin-left: auto;
    }

    .comment-item .content {
        font-size: 14px;
        color: #666;
        line-height: 22px;
        word-break: break-word;
    }

    .actions {
        margin-top: 10px;
        font-size: 13px;
        color: #ffc210;
    }

    .actions span {
        cursor: pointer;
        margin-right: 16px;
    }

    .actions .delete {
        color: #fa6240;
    }

    .reply-list {
        margin-top: 14px;
        padding: 12px 14px;
        background: #fafafa;
        border-radius: 4px;
    }

    .reply-item {
        display: flex;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }

    .reply-item:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }

    .reply-to {
        color: #ffc210;
        font-size: 12px;
        margin: 0 8px;
    }

    .sub-replies {
        margin-left: 28px;
        margin-top: 8px;
        padding-left: 12px;
        border-left: 2px solid #f0f0f0;
    }

    .sub-replies .reply-item {
        padding: 6px 0;
    }

    .sub-replies .avatar.small {
        width: 26px;
        height: 26px;
    }

    .reply-actions {
        margin-top: 8px;
        font-size: 13px;
    }

    .reply-actions span {
        color: #ffc210;
        cursor: pointer;
        margin-right: 16px;
    }

    .reply-actions .collapse {
        color: #9b9b9b;
    }
</style>
