<template>
    <div class="course_pagination block">
        <el-pagination
            :current-page="page"
            :page-size="pageSize"
            :page-sizes="pageSizes"
            :total="total"
            layout="sizes, prev, pager, next"
            @current-change="$emit('current-change', $event)"
            @size-change="$emit('size-change', $event)"
        />
    </div>
</template>

<script>
export default {
    name: 'CoursePagination',
    props: {
        total: {
            type: Number,
            required: true,
        },
        page: {
            type: Number,
            required: true,
        },
        pageSize: {
            type: Number,
            required: true,
        },
        pageSizes: {
            type: Array,
            default () {
                return [2, 3, 5, 10]
            },
        },
    },
}
</script>
