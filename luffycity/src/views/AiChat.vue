<template>
    <div class="ai-chat">
        <div class="main">
            <!-- 模式切换 -->
            <div class="mode-tabs">
                <span :class="{active: mode==='chat'}" @click="switchMode('chat')">
                    <i class="el-icon-chat-dot-round"></i> 普通闲聊
                </span>
                <span :class="{active: mode==='course'}" @click="switchMode('course')">
                    <i class="el-icon-reading"></i> 课程问答
                </span>
            </div>

            <!-- 聊天区域 -->
            <div class="chat-area" ref="chatArea">
                <div v-if="messages.length === 0" class="welcome">
                    <img src="@/assets/img/head-logo.svg" alt="" class="welcome-logo">
                    <p class="welcome-title">Hi，我是 Luffy AI 助手</p>
                    <p class="welcome-hint" v-if="mode==='chat'">你可以问我任何问题~</p>
                    <p class="welcome-hint" v-else>试试问我"Python怎么入门"、"有什么前端课程"</p>
                </div>

                <div v-for="(msg, idx) in messages" :key="idx" class="message-item">
                    <!-- 用户消息 -->
                    <div class="user-msg">
                        <div class="msg-bubble user-bubble">{{ msg.question }}</div>
                    </div>
                    <!-- AI 回答 -->
                    <div class="ai-msg">
                        <div class="msg-bubble ai-bubble">
                            <div v-if="msg.error" class="error-text">{{ msg.answer }}</div>
                            <div v-else class="markdown-body" v-html="renderMarkdown(msg.answer)"></div>
                        </div>
                        <!-- 参考来源 (仅课程问答模式) -->
                        <div v-if="msg.sources && msg.sources.length" class="sources">
                            <p class="sources-title">参考来源：</p>
                            <span class="source-tag" v-for="(s, i) in msg.sources" :key="i">
                                {{ s.course_name }}
                                <span v-if="s.section_name"> → {{ s.section_name }}</span>
                                <em>相似度 {{ s.score }}</em>
                            </span>
                        </div>
                    </div>
                </div>

                <!-- 加载状态 -->
                <div v-if="loading" class="loading">
                    <i class="el-icon-loading"></i> AI 思考中...
                </div>
            </div>

            <!-- 输入区域 -->
            <div class="input-area">
                <el-input
                    v-model="inputText"
                    :placeholder="mode==='chat' ? '随便聊聊...' : '输入课程相关问题...'"
                    :disabled="loading"
                    @keyup.enter.native="send"
                    size="large"
                    clearable
                >
                    <el-button slot="append" icon="el-icon-s-promotion" @click="send" :disabled="loading || !inputText.trim()">发送</el-button>
                </el-input>
            </div>
        </div>
    </div>
</template>

<script>
    import DOMPurify from 'dompurify'
    import { marked } from "marked"

    export default {
        name: "AiChat",
        components: {
        },
        data() {
            return {
                mode: 'chat',
                inputText: '',
                messages: [],
                loading: false,
            }
        },
        methods: {
            switchMode(mode) {
                this.mode = mode;
                this.messages = [];  // 切换模式清空历史，避免闲聊上下文干扰课程问答
            },
            renderMarkdown (text) {
                if (!text) return '';
                const raw = marked.parse(text, { async: false })
                return DOMPurify.sanitize(raw)
            },
            async send() {
                const question = this.inputText.trim();
                if (!question || this.loading) return;

                const api_path = this.mode === 'chat' ? 'ai/chat/stream/' : 'ai/course/stream/';
                const url = `${this.$settings.stream_base_url}${api_path}`;

                this.loading = true;
                this.inputText = '';

                this.messages.push({
                    question: question,
                    answer: '',
                    sources: [],
                    error: false,
                });
                const currentMsg = this.messages[this.messages.length - 1];

                this.$nextTick(() => { this.scrollToBottom(); });

                // 构建对话历史：取最近 6 轮已完成的问答
                const history = [];
                const recent = this.messages.slice(-7, -1);  // 去掉刚加的占位消息
                for (const msg of recent) {
                    if (msg.answer && !msg.error) {
                        history.push({ role: 'user', content: msg.question });
                        history.push({ role: 'assistant', content: msg.answer });
                    }
                }

                // 构建请求头：带上 JWT token
                const headers = { 'Content-Type': 'application/json' };
                const token = this.$cookies.get('token');
                if (token) {
                    headers['Authorization'] = 'jwt ' + token;
                }

                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify({ message: question, history: history }),
                    });

                    if (response.status === 429) {
                        const errorBody = await response.json();
                        currentMsg.answer = errorBody.msg || '请求太频繁，请稍后再试';
                        currentMsg.error = true;
                        return;
                    }

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    // 逐行读取 SSE 流
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });
                        // SSE 事件以 \n\n 分隔
                        const parts = buffer.split('\n\n');
                        buffer = parts.pop();  // 最后一个可能不完整，保留

                        for (const part of parts) {
                            const line = part.trim();
                            if (!line || !line.startsWith('data: ')) continue;

                            try {
                                const event = JSON.parse(line.slice(6));
                                if (event.content) {
                                    currentMsg.answer += event.content;
                                    this.$nextTick(() => { this.scrollToBottom(); });
                                }
                                if (event.done) {
                                    currentMsg.sources = event.sources || [];
                                }
                            } catch (e) {
                                // 解析失败的行跳过
                            }
                        }
                    }
                } catch (e) {
                    if (!currentMsg.answer) {
                        currentMsg.answer = '网络请求失败，请检查网络连接';
                        currentMsg.error = true;
                    }
                } finally {
                    this.loading = false;
                    this.$nextTick(() => { this.scrollToBottom(); });
                }
            },
            scrollToBottom() {
                const el = this.$refs.chatArea;
                if (el) {
                    el.scrollTop = el.scrollHeight;
                }
            },
        },
    }
</script>

<style scoped>
    .ai-chat {
        background: #f6f6f6;
        min-height: 100vh;
    }

    .main {
        width: 900px;
        margin: 35px auto 0;
        padding-bottom: 40px;
    }

    /* ===== 模式切换 ===== */
    .mode-tabs {
        text-align: center;
        margin-bottom: 20px;
    }

    .mode-tabs span {
        display: inline-block;
        font-size: 16px;
        padding: 10px 35px;
        margin: 0 10px;
        cursor: pointer;
        color: #666;
        border-bottom: 2px solid transparent;
        transition: all .3s ease;
    }

    .mode-tabs span:hover {
        color: orange;
    }

    .mode-tabs span.active {
        color: #ffc210;
        border-bottom-color: #ffc210;
    }

    /* ===== 聊天区域 ===== */
    .chat-area {
        background: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        min-height: 450px;
        max-height: 550px;
        overflow-y: auto;
        padding: 30px 40px;
        margin-bottom: 20px;
    }

    .welcome {
        text-align: center;
        padding-top: 120px;
    }

    .welcome-logo {
        width: 80px;
        height: auto;
        margin-bottom: 20px;
        opacity: 0.5;
    }

    .welcome-title {
        font-size: 22px;
        color: #333;
        margin-bottom: 10px;
    }

    .welcome-hint {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* 消息气泡 */
    .message-item {
        margin-bottom: 30px;
    }

    .msg-bubble {
        display: inline-block;
        max-width: 75%;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 15px;
        line-height: 1.8;
        word-break: break-word;
    }

    .user-msg {
        text-align: right;
        margin-bottom: 12px;
    }

    .user-bubble {
        background: #ecf5ff;
        color: #333;
        text-align: left;
    }

    .ai-msg {
        text-align: left;
    }

    .ai-bubble {
        background: #f5f5f5;
        color: #333;
    }

    .error-text {
        color: #f56c6c;
    }

    /* Markdown 渲染样式 */
    .markdown-body >>> h1, .markdown-body >>> h2, .markdown-body >>> h3 {
        font-size: 16px;
        font-weight: bold;
        margin: 8px 0 4px;
    }

    .markdown-body >>> p {
        margin: 4px 0;
    }

    .markdown-body >>> ul, .markdown-body >>> ol {
        padding-left: 20px;
        margin: 4px 0;
    }

    .markdown-body >>> li {
        margin: 2px 0;
    }

    .markdown-body >>> code {
        background: #e8e8e8;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 13px;
        font-family: Consolas, Monaco, monospace;
    }

    .markdown-body >>> pre {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 12px 16px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 8px 0;
    }

    .markdown-body >>> pre code {
        background: transparent;
        padding: 0;
        color: inherit;
    }

    .markdown-body >>> strong {
        font-weight: bold;
    }

    .markdown-body >>> table {
        border-collapse: collapse;
        width: 100%;
        margin: 8px 0;
    }

    .markdown-body >>> th, .markdown-body >>> td {
        border: 1px solid #ddd;
        padding: 6px 10px;
        text-align: left;
    }

    .markdown-body >>> th {
        background: #f5f5f5;
    }

    .markdown-body >>> blockquote {
        border-left: 3px solid #ffc210;
        padding-left: 12px;
        margin: 8px 0;
        color: #666;
    }

    /* 参考来源 */
    .sources {
        margin-top: 10px;
    }

    .sources-title {
        font-size: 13px;
        color: #9b9b9b;
        margin-bottom: 6px;
    }

    .source-tag {
        display: inline-block;
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        padding: 4px 10px;
        margin-right: 8px;
        margin-bottom: 6px;
        font-size: 13px;
        color: #666;
    }

    .source-tag em {
        font-style: normal;
        color: #ffc210;
        margin-left: 4px;
    }

    /* 加载 */
    .loading {
        color: #9b9b9b;
        font-size: 14px;
        padding: 10px 0;
    }

    .loading i {
        margin-right: 6px;
    }

    /* ===== 输入区域 ===== */
    .input-area {
        background: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 4px 0 #f0f0f0;
        padding: 20px 30px;
    }
</style>
