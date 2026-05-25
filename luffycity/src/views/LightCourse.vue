<template>
    <CourseCatalog :initial-page-size="10">
        <template #top>
            <el-alert
                title="轻课与实战课共用同一课程库展示，此处为在线列表；后端若拆分轻课类型后可在筛选中单独呈现。"
                type="info"
                show-icon
                :closable="false"
            />
        </template>
    </CourseCatalog>
</template>

<script>
import CourseCatalog from '@/components/CourseCatalog.vue'

export default {
    name: 'LightCourseUi',
    components: { CourseCatalog },
}
</script>
