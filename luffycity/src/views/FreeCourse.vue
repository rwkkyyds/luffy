<template>
    <div class="course course_free">
        <div class="main">
            <div class="free-head">
                <h2>免费公开课</h2>
                <p>以下为系统内售价为 0 元的课程。</p>
            </div>

            <el-skeleton v-if="loading" :rows="8" animated />
            <div v-else-if="course_list.length" class="course-list">
                <CourseCard
                    v-for="course in course_list"
                    :key="course.id"
                    :course="course"
                    :show-sections="false"
                    buy-label="立即学习"
                >
                    <template slot="pay">
                        <span class="discount-price">¥0</span>
                        <span class="buy-now">立即学习</span>
                    </template>
                </CourseCard>
            </div>
            <div v-else class="empty">暂无标价 0 元的免费课程。</div>
        </div>
    </div>
</template>

<script>
import { api } from '@/api'
import CourseCard from '@/components/CourseCard.vue'

export default {
    name: 'FreeCourse',
    components: { CourseCard },
    data () {
        return {
            course_list: [],
            loading: true,
        }
    },
    created () {
        api.course.actualList({ page_size: 50, page: 1, ordering: '-students' })
            .then(response => {
                const rows = response.data.results || []
                this.course_list = rows.filter(c => Number.parseFloat(String(c.price)) === 0)
            })
            .catch(() => {
                this.$message.error('加载免费课程失败')
            })
            .finally(() => {
                this.loading = false
            })
    },
}
</script>

<style scoped>
.free-head {
    width: 1100px;
    margin: 35px auto 20px;
    padding: 20px;
    background: #fff;
    border-radius: 4px;
}

.free-head h2 {
    margin: 0 0 8px;
    font-weight: normal;
    color: #333;
}

.free-head p {
    margin: 0;
    font-size: 14px;
    color: #9b9b9b;
}

.main {
    width: 1100px;
    margin: 0 auto;
    padding-bottom: 40px;
}

.empty {
    padding: 60px;
    text-align: center;
    color: #888;
    background: #fff;
    border-radius: 4px;
}
</style>
