<template>
  <div id="app">
    <Header v-if="showChrome"/>
    <router-view/>
    <Footer v-if="showChrome"/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

export default {
    name: 'App',
    components: { Header, Footer },
    computed: {
        showChrome () {
            return this.$route.name !== 'login'
        },
    },
}
</script>
