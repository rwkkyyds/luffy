<template>
    <div class="header">
        <div class="slogan">
            <p>老男孩IT教育 | 帮助有志向的年轻人通过努力学习获得体面的工作和生活</p>
        </div>
        <div class="nav">
            <ul class="left-part">
                <li class="logo">
                    <router-link to="/home">
                        <img src="../assets/img/head-logo.svg" alt="">
                    </router-link>
                </li>
                <li class="ele">
                    <span @click="goPage('/free-course')" :class="{active: url_path === '/free-course'}">免费课</span>
                </li>
                <li class="ele">
                    <span @click="goPage('/actual-course')" :class="{active: url_path === '/actual-course'}">实战课</span>
                </li>
                <li class="ele">
                    <span @click="goPage('/light-course')" :class="{active: url_path === '/light-course'}">轻课</span>
                </li>
                <li class="ele">
                    <span @click="goPage('/ai-chat')" :class="{active: url_path === '/ai-chat'}">AI 问答</span>
                </li>
            </ul>

            <div class="right-part">
                <div class="cart-entry" @click="goPage('/cart')">
                    <img src="../assets/img/cart-yellow.svg" alt="">
                    <span>购物车</span>
                    <em v-if="cartCount > 0">{{ cartCount > 99 ? '99+' : cartCount }}</em>
                </div>
                <div v-if="username" class="cart-entry" @click="goPage('/orders')">
                    <span>我的订单</span>
                </div>
                <div v-if="username" class="user-info">
                    <img class="user-avatar" :src="icon" alt="" @click="goPage('/profile')">
                    <span @click="goPage('/profile')">{{username}}</span>
                    <span class="line">|</span>
                    <span @click="handleLogout">退出</span>
                </div>
                <div v-else>
                    <span @click="put_login">登录</span>
                    <span class="line">|</span>
                    <span @click="put_register">注册</span>
                </div>
            </div>
            <Login v-if="is_login" @close="close_login" @go="put_register"/>
            <Register v-if="is_register" @close="close_register" @go="put_login"/>
            <form class="search" @submit.prevent="search_action(search_word)">
                <div class="tips" v-if="is_search_tip" @mousedown.prevent>
                    <span @click="search_action('Python')">Python</span>
                    <span @click="search_action('Linux')">Linux</span>
                </div>
                <input type="text" :placeholder="search_placeholder" @focus="on_search" @blur="off_search"
                       v-model="search_word">
                <button type="submit" class="glyphicon glyphicon-search"></button>
            </form>


        </div>
    </div>

</template>

<script>
    import { mapState } from 'vuex'
    import { api } from '@/api'
    import Login from "@/components/Login";
    import Register from "@/components/Register";

    export default {
        name: "Header",
        data () {
            return {
                url_path: sessionStorage.url_path || '/',
                is_login: false,
                is_register: false,
                is_search_tip: true,
                search_placeholder: '',
                search_word: '',
                searchBlurTimer: null,
            }
        },
        computed: {
            ...mapState(['username', 'icon', 'cartCount']),
        },
        watch: {
            username () {
                this.refreshCartCount()
            },
        },
        methods: {
            refreshCartCount () {
                api.cart.list()
                    .then(res => {
                        if (res.data.status === 100) {
                            this.$store.commit('SET_CART_COUNT', res.data.cart_count || 0)
                        }
                    })
                    .catch(() => {})
            },
            goPage (url_path) {
                if (this.$route.path !== url_path) {
                    this.$router.push(url_path);
                }
                sessionStorage.url_path = url_path;
            },
            close_login () {
                this.is_login = false
            },
            close_register () {
                this.is_register = false
            },
            put_register () {
                this.is_register = true
                this.is_login = false
            },
            put_login () {
                this.is_register = false
                this.is_login = true
            },
            async handleLogout () {
                await api.user.logout().catch(() => {})
                this.$store.commit('CLEAR_USER')
            },
            search_action (search_word) {
                if (!search_word) {
                    this.$message('请输入要搜索的内容');
                    return
                }
                if (search_word !== this.$route.query.word) {
                    this.$router.push(`/course/search?word=${search_word}`);
                }
                this.search_word = '';
            },
            on_search () {
                if (this.searchBlurTimer) {
                    clearTimeout(this.searchBlurTimer)
                    this.searchBlurTimer = null
                }
                this.search_placeholder = '请输入想搜索的课程';
                this.is_search_tip = false;
            },
            off_search () {
                if (this.searchBlurTimer) {
                    clearTimeout(this.searchBlurTimer)
                }
                this.searchBlurTimer = setTimeout(() => {
                    this.search_placeholder = '';
                    this.is_search_tip = true;
                    this.searchBlurTimer = null
                }, 200)
            },


        },
        created () {
            sessionStorage.url_path = this.$route.path;
            this.url_path = this.$route.path;
            this.refreshCartCount()
            this.$root.$on('header-open-login', this.put_login)
        },
        beforeDestroy () {
            if (this.searchBlurTimer) {
                clearTimeout(this.searchBlurTimer)
            }
            this.$root.$off('header-open-login', this.put_login)
        },
        components: {
            Login, Register
        }
    }
</script>

<style scoped>
    .header {
        background-color: white;
        box-shadow: 0 0 5px 0 #aaa;
    }

    .header:after {
        content: "";
        display: block;
        clear: both;
    }

    .slogan {
        background-color: #eee;
        height: 40px;
    }

    .slogan p {
        width: 1200px;
        margin: 0 auto;
        color: #aaa;
        font-size: 13px;
        line-height: 40px;
    }

    .nav {
        background-color: white;
        user-select: none;
        width: 1200px;
        margin: 0 auto;

    }

    .nav ul {
        padding: 15px 0;
        float: left;
    }

    .nav ul:after {
        clear: both;
        content: '';
        display: block;
    }

    .nav ul li {
        float: left;
    }

    .logo {
        margin-right: 20px;
    }

    .ele {
        margin: 0 20px;
    }

    .ele span {
        display: block;
        font: 15px/36px '微软雅黑';
        border-bottom: 2px solid transparent;
        cursor: pointer;
    }

    .ele span:hover {
        border-bottom-color: orange;
    }

    .ele span.active {
        color: orange;
        border-bottom-color: orange;
    }

    .right-part {
        float: right;
        display: flex;
        align-items: center;
    }

    .cart-entry {
        position: relative;
        display: flex;
        align-items: center;
        margin-right: 20px;
        cursor: pointer;
        user-select: none;
    }

    .cart-entry img {
        width: 20px;
        height: 18px;
        margin-right: 6px;
    }

    .cart-entry span {
        font-size: 14px;
        color: #4a4a4a;
        line-height: 68px;
    }

    .cart-entry em {
        position: absolute;
        top: 14px;
        left: 14px;
        min-width: 16px;
        height: 16px;
        padding: 0 4px;
        background: #fa6240;
        border-radius: 8px;
        color: #fff;
        font-size: 11px;
        font-style: normal;
        line-height: 16px;
        text-align: center;
    }

    .user-info {
        display: flex;
        align-items: center;
    }

    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 8px;
        cursor: pointer;
    }

    .right-part .line {
        margin: 0 10px;
    }

    .right-part span {
        line-height: 68px;
        cursor: pointer;
    }

    .search {
        float: right;
        position: relative;
        margin-top: 22px;
        margin-right: 10px;
    }

    .search input, .search button {
        border: none;
        outline: none;
        background-color: white;
    }

    .search input {
        border-bottom: 1px solid #eeeeee;
    }

    .search input:focus {
        border-bottom-color: orange;
    }

    .search input:focus + button {
        color: orange;
    }

    .search .tips {
        position: absolute;
        bottom: 3px;
        left: 0;
    }

    .search .tips span {
        border-radius: 11px;
        background-color: #eee;
        line-height: 22px;
        display: inline-block;
        padding: 0 7px;
        margin-right: 3px;
        cursor: pointer;
        color: #aaa;
        font-size: 14px;

    }

    .search .tips span:hover {
        color: orange;
    }
</style>