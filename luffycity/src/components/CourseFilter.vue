<template>
    <div class="condition">
        <ul class="cate-list">
            <li class="title">课程分类:</li>
            <li :class="filter.course_category === 0 ? 'this' : ''" @click="filter.course_category = 0">全部</li>
            <li
                v-for="category in categoryList"
                :key="'c-' + category.id"
                :class="filter.course_category === category.id ? 'this' : ''"
                @click="filter.course_category = category.id"
            >
                {{ category.name }}
            </li>
        </ul>

        <div class="ordering">
            <ul>
                <li class="title">筛&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;选:</li>
                <li
                    class="default"
                    :class="filter.ordering === 'id' || filter.ordering === '-id' ? 'this' : ''"
                    @click="filter.ordering = '-id'"
                >
                    默认
                </li>
                <li
                    class="hot"
                    :class="filter.ordering === 'students' || filter.ordering === '-students' ? 'this' : ''"
                    @click="toggleStudents"
                >
                    人气
                </li>
                <li
                    class="price"
                    :class="
                        filter.ordering === 'price'
                            ? 'price_up this'
                            : filter.ordering === '-price'
                              ? 'price_down this'
                              : ''
                    "
                    @click="togglePrice"
                >
                    价格
                </li>
            </ul>
            <p class="condition-result">共{{ courseTotal }}个课程</p>
        </div>
    </div>
</template>

<script>
export default {
    name: 'CourseFilter',
    props: {
        categoryList: {
            type: Array,
            default () {
                return []
            },
        },
        courseTotal: {
            type: Number,
            default: 0,
        },
        /** 与父组件共享的可变筛选对象（按址修改） */
        filter: {
            type: Object,
            required: true,
        },
    },
    methods: {
        toggleStudents () {
            this.filter.ordering = this.filter.ordering === '-students' ? 'students' : '-students'
        },
        togglePrice () {
            this.filter.ordering = this.filter.ordering === '-price' ? 'price' : '-price'
        },
    },
}
</script>
