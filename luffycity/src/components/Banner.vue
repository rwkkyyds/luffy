<template>
    <div class="banner">
        <el-carousel :interval="5000" arrow="always" height="400px">
            <el-carousel-item v-for="(item, index) in banner_list" :key="item.link || `banner-${index}`">
                <!-- 外链用 <a>，站内路径用 router-link；link 为空时不要用 indexOf 以免抛错 -->
                <div v-if="!isExternalLink(item.link)">
                    <router-link :to="item.link || '/'">
                        <img :src="mediaSrc(item.image)" :alt="item.title || 'banner'" />
                    </router-link>
                </div>
                <div v-else>
                    <a :href="item.link" rel="noopener noreferrer">
                        <img :src="mediaSrc(item.image)" :alt="item.title || 'banner'" />
                    </a>
                </div>


            </el-carousel-item>
        </el-carousel>
    </div>
</template>

<script>
    import { api } from '@/api'
    import { normalizeMediaSrc } from '@/utils/media'

    export default {
        name: "Banner",
        data () {
            return {
                banner_list: []
            }
        },
        methods: {
            isExternalLink (link) {
                if (link == null || link === '') return false
                return /^https?:\/\//i.test(String(link))
            },
            mediaSrc (url) {
                return normalizeMediaSrc(url)
            },
        },
        created () {
            api.home.banner()
                .then(res => {
                    const body = res && res.data
                    // status 后端为数字；用 == 避免极端情况下类型不一致
                    if (body && body.status == 100 && Array.isArray(body.result)) {
                        this.banner_list = body.result
                        if (process.env.NODE_ENV === 'development') {
                            // eslint-disable-next-line no-console
                            console.log('[banner]', this.banner_list)
                        }
                    }
                })
                .catch(err => {
                    if (process.env.NODE_ENV === 'development') {
                        // eslint-disable-next-line no-console
                        console.warn('[banner] request failed', err)
                    }
                })
        },
    }
</script>

<style scoped>


    el-carousel-item {
        height: 400px;
        min-width: 1200px;
    }

    .el-carousel__item img {
        height: 400px;
        margin-left: calc(50% - 1920px / 2);
    }
</style>