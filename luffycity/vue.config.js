const { defineConfig } = require('@vue/cli-service')
const CompressionWebpackPlugin = require('compression-webpack-plugin')

/**
 * 开发阶段代理目标：Django runserver 的地址（默认 8000）。
 *
 * 常见误解：浏览器里打开的是「前端」地址，例如 http://127.0.0.1:8080，
 * 若 8080 被占用，CLI 会自动改成 8081、8082——那是「本机前端 devServer 端口」，
 * 不是后端。下面 target 才是后端，应始终指向 Django（8000），不是 8082。
 *
 * 后端改端口时：在 .env.development 里写 DJANGO_DEV_TARGET=http://127.0.0.1:你想要的端口
 */
const DJANGO_DEV_TARGET = (process.env.DJANGO_DEV_TARGET || 'http://127.0.0.1:8000').replace(/\/$/, '')

module.exports = defineConfig({
    transpileDependencies: true,
    productionSourceMap: false,
    // Windows + 新版本 Node 上多进程并行偶尔卡在 “Starting development server...”
    parallel: false,
    devServer: {
        host: '127.0.0.1',
        port: 8080,
        hot: true,
        // 浏览器访问的是「前端端口」(port，常见 8080；被占用会变成 8081/8082)。
        // 下面 proxy 把以 /api、/media 开头的请求转发到「后端」DJANGO_DEV_TARGET（默认 8000）。
        proxy: {
            '/api': {
                target: DJANGO_DEV_TARGET,
                changeOrigin: true,
            },
            '/media': {
                target: DJANGO_DEV_TARGET,
                changeOrigin: true,
            },
        },
    },
    lintOnSave: process.env.NODE_ENV !== 'production',
    configureWebpack: config => {
        if (process.env.NODE_ENV !== 'production') return
        config.plugins.push(
            new CompressionWebpackPlugin({
                algorithm: 'gzip',
                test: /\.(js|css|html|svg)$/,
                threshold: 10240,
                minRatio: 0.8,
            })
        )
    },
})
