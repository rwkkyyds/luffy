<template>
    <div class="home">
        <Banner/>

        <div class="course-section">
            <h2 class="section-title">热门推荐</h2>
            <el-skeleton v-if="loading" :rows="4" animated/>
            <div v-else-if="recommended.length" class="course-grid">
                <el-card v-for="course in recommended" :key="course.id" :body-style="{ padding: '0px' }" class="course_card">
                    <router-link :to="'/actual/detail/'+course.id">
                        <img :src="course.course_img" class="image" alt="">
                    </router-link>
                    <div class="card-body">
                        <router-link :to="'/actual/detail/'+course.id" class="course-title-link">
                            {{ course.name }}
                        </router-link>
                        <div class="bottom">
                            <span class="time">{{ course.students }}人在学 · ¥{{ course.price }}</span>
                            <router-link :to="'/actual/detail/'+course.id" class="detail-link">查看详情</router-link>
                        </div>
                    </div>
                </el-card>
            </div>
            <p v-else class="empty-tip">暂无推荐课程，请稍后再试。</p>
        </div>
        <img src="@/assets/img/bottom.png" alt="" height="500px"
             width="100%" loading="lazy">
    </div>
</template>

<script>
    import { api } from '@/api'
    import Banner from "@/components/Banner";

    export default {
        name: 'HomeView',
        data () {
            return {
                recommended: [],
                loading: true,
            }
        },
        created () {
            api.course.actualList({ page: 1, page_size: 8, ordering: '-students' })
                .then(res => {
                    this.recommended = res.data.results || []
                })
                .catch(() => {
                    this.$message.error('加载推荐课程失败')
                })
                .finally(() => {
                    this.loading = false
                })
        },
        components: {
            Banner,
        },
    }
</script>

<style scoped>
    .course-section {
        width: 1200px;
        margin: 40px auto 0;
    }

    .section-title {
        font-size: 24px;
        color: #333;
        margin-bottom: 24px;
        padding-left: 10px;
        border-left: 4px solid #ffc210;
    }

    .course-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
    }

    .course_card {
        width: 282px;
        border-radius: 6px;
        overflow: hidden;
        transition: box-shadow 0.2s;
    }

    .course_card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    .image {
        width: 100%;
        height: 155px;
        object-fit: cover;
        display: block;
    }

    .card-body {
        padding: 14px;
    }

    .course-title-link {
        font-size: 14px;
        color: #333;
        text-decoration: none;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.4;
        min-height: 39px;
    }

    .course-title-link:hover {
        color: #ffc210;
    }

    .bottom {
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .time {
        font-size: 13px;
        color: #999;
    }

    .detail-link {
        font-size: 13px;
        color: #ffc210;
        text-decoration: none;
    }

    .detail-link:hover {
        text-decoration: underline;
    }

    .empty-tip {
        text-align: center;
        padding: 60px 0;
        color: #999;
        font-size: 15px;
    }
</style>
