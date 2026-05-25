"""
智谱 GLM 大模型客户端封装
这个文件的作用：
- 把调用智谱 API 的代码封装成一个类
- 其他地方只需要 import 这个类就能用
- 方便以后换成其他大模型（只改这一个文件）
"""
import requests  # 用来发 HTTP 请求，就像 postman 一样
class ZhipuClient:
    """
    智谱 GLM 客户端
    
    使用方法：
        client = ZhipuClient(api_key="你的key")
        answer = client.chat("你好")
        print(answer)
    """
    
    def __init__(self, api_key: str):
        """
        初始化客户端
        
        参数:
            api_key: 智谱开放平台的 API Key
        """
        self.api_key = api_key
        # 智谱 API 的地址（固定的，不用改）
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    def chat(self, user_message: str, system_prompt: str = None, history: list = None) -> str:
        """
        发送消息给 AI，获取回复

        参数:
            user_message: 用户的问题
            system_prompt: 系统提示词
            history: 对话历史，格式 [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}, ...]

        返回:
            AI 的回答文本
        """

        # ========== 第一步：构建消息列表 ==========
        messages = []

        # 系统提示词（人设）
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # 历史对话（多轮对话的关键——把之前说的也带上）
        if history:
            # 只取最近 12 条（6 轮），防止 token 超限
            messages.extend(history[-12:])  # 最近 6 轮
            #把取出的这 12 个元素逐个追加到 messages 列表末尾，不是整体作为一个元素添加,平铺加入。

        # 当前用户问题
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # ========== 第二步：构建请求参数 ==========
        # 这是发给智谱 API 的 JSON 数据
        payload = {
            "model": "glm-4-flash",         # 使用的模型，flash 版本免费且快
            "messages": messages,           # 上面构建的消息列表
            "temperature": 0.3,             # 控制回答的随机性，0-1，越低越严谨
            "max_tokens": 1024,             # 最大回复长度（token 数）
        }
        
        # 请求头，带上 API Key 做身份验证
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"   # Bearer 是固定格式
        }
        
        # ========== 第三步：发送请求 ==========
        try:
            # 发送 POST 请求到智谱 API
            response = requests.post(
                self.base_url,
                json=payload,               # 自动转成 JSON 格式
                headers=headers,
                timeout=60                  # 超时时间 60 秒
            )
            
            # 检查 HTTP 状态码
            response.raise_for_status()     # 如果不是 200，会抛出异常
            
            # ========== 第四步：解析响应 ==========
            result = response.json()
            
            # 智谱返回的数据结构：
            # {
            #     "choices": [
            #         {
            #             "message": {
            #                 "role": "assistant",
            #                 "content": "AI的回答内容"
            #             }
            #         }
            #     ]
            # }
            
            # 提取 AI 的回答
            answer = result["choices"][0]["message"]["content"]
            return answer
            
        except requests.exceptions.Timeout:
            return "抱歉，AI 响应超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return f"抱歉，AI 服务出错：{str(e)}"
        except (KeyError, IndexError) as e:
            return f"抱歉，解析 AI 响应失败：{str(e)}"

    def chat_stream(self, user_message: str, system_prompt: str = None, history: list = None):
        """
        流式聊天 —— 返回生成器，逐块 yield 文本

        参数:
            user_message: 用户问题
            system_prompt: 系统提示词
            history: 对话历史，传入前几轮 user/assistant 消息
        """
        import json as _json

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history[-12:])  # 最近 6 轮
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": "glm-4-flash",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
            "stream": True,              # 开启流式输出
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(
            self.base_url,
            json=payload,
            headers=headers,
            stream=True,                 # requests 库的流式读取，不一次性加载响应体
            timeout=60
        )
        response.raise_for_status()

        # 逐行读取 SSE 响应
        # 智谱返回格式：data: {"choices":[{"delta":{"content":"文本"}}]}\n\n
        # response.iter_lines:按换行符切割响应内容，一行一行返回
        # decode_unicode=True:自动将字节流（bytes）解码为字符串（str）
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data: "):
                continue
            data_str = line[6:]          # 去掉 "data: " 前缀
            if data_str == "[DONE]":     # 流结束标记
                break
            try:
                chunk = _json.loads(data_str)
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content
            except (_json.JSONDecodeError, KeyError, IndexError):
                continue


# ========== 测试代码 ==========
# 如果直接运行这个文件，会执行下面的测试
if __name__ == "__main__":
    import os
    import sys

    API_KEY = os.environ.get("ZHIPU_API_KEY", "").strip()
    if not API_KEY:
        print("请设置环境变量 ZHIPU_API_KEY")
        sys.exit(1)

    client = ZhipuClient(api_key=API_KEY)
    
    # 测试一下
    answer = client.chat("你好你是什么大模型？")
    print("AI 回答：", answer)
