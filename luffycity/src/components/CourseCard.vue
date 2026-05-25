<template>
    <div class="course-item">
        <div class="course-image">
            <router-link :to="detailPath">
                <img :src="course.course_img" :alt="course.name" loading="lazy">
            </router-link>
        </div>
        <div class="course-info">
            <h3>
                <router-link :to="detailPath">{{ course.name }}</router-link>
                <span><img src="@/assets/img/avatar1.svg" alt="">{{ course.students }}人已加入学习</span>
            </h3>
            <p class="teather-info">
                {{ teacherName }} {{ teacherTitle }} {{ teacherSignature }}
                <span v-if="course.sections > course.pub_sections">共{{ course.sections }}课时/已更新{{ course.pub_sections }}课时</span>
                <span v-else>共{{ course.sections }}课时/更新完成</span>
            </p>
            <ul v-if="showSections && sections.length" class="section-list">
                <li v-for="(section, key) in sections" :key="`${section.name}-${key}`">
                    <span class="section-title">0{{ key + 1 }} | {{ section.name }}</span>
                    <span v-if="section.free_trail" class="free">免费</span>
                </li>
            </ul>
            <div class="pay-box">
                <slot name="pay">
                    <template v-if="course.discount_type">
                        <span class="discount-type">{{ course.discount_type }}</span>
                        <span class="discount-price">￥{{ course.real_price }}元</span>
                        <span class="original-price">原价：{{ course.price }}元</span>
                    </template>
                    <span v-else class="discount-price">￥{{ course.price }}元</span>
                    <span class="buy-now" @click="handleBuy">{{ buyLabel }}</span>
                </slot>
            </div>
        </div>
    </div>
</template>

<script>
import { api } from '@/api'

export default {
    name: 'CourseCard',
    props: {
        course: {
            type: Object,
            required: true,
        },
        showSections: {
            type: Boolean,
            default: true,
        },
        /** 详情路径前缀，不带尾部斜杠，如 /actual/detail */
        detailPrefix: {
            type: String,
            default: '/actual/detail',
        },
        buyLabel: {
            type: String,
            default: '加入购物车',
        },
    },
    computed: {
        sections () {
            return this.course.section_list || []
        },
        teacherName () {
            return (this.course.teacher && this.course.teacher.name) || ''
        },
        teacherTitle () {
            return (this.course.teacher && this.course.teacher.title) || ''
        },
        teacherSignature () {
            return (this.course.teacher && this.course.teacher.signature) || ''
        },
        detailPath () {
            const base = this.detailPrefix.replace(/\/$/, '')
            return `${base}/${this.course.id}`
        },
    },
    methods: {
        handleBuy () {
            const price = this.course.real_price || this.course.price
            if (!price) {
                this.$message.warning('课程信息加载中')
                return
            }
            api.cart.add({
                course_id: Number(this.course.id),
                price: price,
            })
                .then(res => {
                    if (res.data.status === 100) {
                        this.$message.success('已加入购物车')
                        this.$store.commit('SET_CART_COUNT', res.data.cart_count)
                    } else {
                        this.$message.warning(res.data.msg || '添加失败')
                    }
                })
                .catch(() => {
                    this.$message.error('请求失败')
                })
        },
    },
}
</script>
