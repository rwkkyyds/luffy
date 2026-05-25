module.exports = {
    root: true,
    env: {
        browser: true,
        node: true,
        es2021: true,
    },
    extends: ['plugin:vue/recommended', 'eslint:recommended', 'prettier'],
    parser: 'vue-eslint-parser',
    parserOptions: {
        parser: '@babel/eslint-parser',
        ecmaVersion: 2021,
        sourceType: 'module',
        requireConfigFile: false,
        babelOptions: {
            presets: [require.resolve('@vue/cli-plugin-babel/preset')],
        },
    },
    rules: {
        'vue/multi-word-component-names': 'off',
        'vue/no-reserved-component-names': 'off',
        'vue/no-mutating-props': 'off',
        'vue/no-v-html': 'warn',
        'vue/attributes-order': 'warn',
        'vue/order-in-components': 'warn',
        'vue/first-attribute-linebreak': 'warn',
        'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
        'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-constant-condition': ['error', { checkLoops: false }],
    },
}
