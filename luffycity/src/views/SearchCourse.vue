<template>
    <div class="search-course course">
        <div class="main">
            <div v-if="course_list.length > 0" class="course-list">
                <CourseCard
                    v-for="course in course_list"
                    :key="course.id"
                    :course="course"
                />
            </div>
            <div v-else style="text-align: center; line-height: 60px">
                没有搜索结果
            </div>

            <CoursePagination
                :total="course_total"
                :page="filter.page"
                :page-size="filter.page_size"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
        </div>
    </div>
</template>

<script>
import { api } from '@/api'
import CourseCard from '@/components/CourseCard.vue'
import CoursePagination from '@/components/CoursePagination.vue'

export default {
    name: 'SearchCourse',
    components: {
        CourseCard,
        CoursePagination,
    },
    data () {
        return {
            course_list: [],
            course_total: 0,
            filter: {
                page_size: 10,
                page: 1,
                search: '',
            },
        }
    },
    watch: {
        '$route.query' () {
            this.filter.page = 1
            this.get_course()
        },
    },
    created () {
        this.get_course()
    },
    methods: {
        handleSizeChange (val) {
            this.filter.page = 1
            this.filter.page_size = val
            this.get_course()
        },
        handleCurrentChange (val) {
            this.filter.page = val
            this.get_course()
        },
        get_course () {
            this.filter.search = this.$route.query.word

            api.course.search(this.filter).then(response => {
                this.course_list = response.data.results
                this.course_total = response.data.count
            }).catch(() => {
                this.$message({
                    message: '获取课程信息有误，请联系客服工作人员',
                })
            })
        },
    },
}
</script>
