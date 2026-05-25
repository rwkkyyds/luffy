<template>
    <div class="course">
        <div class="main">
            <div v-if="$slots.top" class="catalog-top">
                <slot name="top" />
            </div>

            <CourseFilter
                :category-list="category_list"
                :course-total="course_total"
                :filter="filter"
            />

            <el-skeleton v-if="list_loading" animated :rows="8" />
            <div v-else class="course-list">
                <CourseCard
                    v-for="item in course_list"
                    :key="item.id"
                    :course="item"
                    :show-sections="true"
                />
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
import CourseFilter from '@/components/CourseFilter.vue'
import CoursePagination from '@/components/CoursePagination.vue'

export default {
    name: 'CourseCatalog',
    components: {
        CourseCard,
        CourseFilter,
        CoursePagination,
    },
    props: {
        initialPageSize: {
            type: Number,
            default: 2,
        },
    },
    data () {
        return {
            list_loading: true,
            category_list: [],
            course_list: [],
            course_total: 0,
            filter: {
                course_category: 0,
                ordering: '-id',
                page_size: this.initialPageSize,
                page: 1,
            },
        }
    },
    watch: {
        'filter.course_category' () {
            this.filter.page = 1
            this.get_course()
        },
        'filter.ordering' () {
            this.get_course()
        },
    },
    created () {
        this.filter.page_size = this.initialPageSize
        this.get_category()
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
        get_category () {
            api.course
                .category()
                .then(response => {
                    this.category_list = response.data
                })
                .catch(() => {
                    this.$message({
                        message: '获取课程分类信息有误，请联系客服工作人员',
                    })
                })
        },
        get_course () {
            this.list_loading = true
            const filters = {
                ordering: this.filter.ordering,
            }
            if (this.filter.course_category > 0) {
                filters.course_category = this.filter.course_category
            }
            if (this.filter.page_size > 0) {
                filters.page_size = this.filter.page_size
            } else {
                filters.page_size = 5
            }
            filters.page = this.filter.page > 1 ? this.filter.page : 1

            api.course
                .actualList(filters)
                .then(response => {
                    this.course_list = response.data.results || []
                    this.course_total = response.data.count ?? 0
                })
                .catch(() => {
                    this.$message({
                        message: '获取课程信息有误，请联系客服工作人员',
                    })
                })
                .finally(() => {
                    this.list_loading = false
                })
        },
    },
}
</script>

<style scoped>
.catalog-top {
    margin-bottom: 18px;
}
</style>
