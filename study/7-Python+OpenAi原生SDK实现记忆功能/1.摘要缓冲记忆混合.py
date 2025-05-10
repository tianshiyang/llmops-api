#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/10 21:43
@Author  : tianshiyang
@File    : 1.摘要缓冲记忆混合.py
"""
import os
from typing import Any

import dotenv
from openai import OpenAI

dotenv.load_dotenv()


# 1.max_tokens用于判断是否需要生成新的摘要
# 2.summary用于存储摘要的信息
# 3.chat_histories用于存储历史对话
# 4.get_num_tokens用于计算传入文本的token数
# 5.save_context用于存储新的交流对话
# 6.get_buffer_string用于将历史对话转换成字符串
# 7.load_memory_variables用于加载记忆变量信息
# 8.summary_text用于将旧的摘要和传入的对话生成新摘要

class ConversationSummaryBufferMemory:
    def __init__(self, max_tokens: int = 300, chat_histories: list = None, summary: str = ""):
        self.max_tokens = max_tokens
        self.chat_histories = [] if chat_histories is None else chat_histories
        self.summary = summary
        self._client = OpenAI(
            base_url=os.environ['OPENAI_BASE_URL'],
            api_key=os.environ["OPENAI_API_KEY"],
        )

    @classmethod
    def get_num_tokens(cls, _query: str) -> int:
        # 获取用户输入的token
        return len(_query)

    def save_context(self, human_query: str, ai_content: str):
        """保存传入的新一次对话信息"""
        self.chat_histories.append({
            "ai": ai_content,
            "human": human_query
        })

        buffer_str = self.get_buffer_string()

        tokens = self.get_num_tokens(buffer_str)

        if tokens > self.max_tokens:
            print("新摘要生成中~")
            self.summary = self.summary_text(self.chat_histories[0])
            print("新摘要生成成功:", self.summary)
            del self.chat_histories[0]

    def get_buffer_string(self) -> str:
        # 将历史对话转化成字符串
        buffer = ""
        for history in self.chat_histories:
            buffer += f"human {history.get('human')} \n ai {history.get('ai')}"
        return buffer.strip()

    def load_memory_variables(self) -> dict[str, Any]:
        """加载记忆变量为一个字典，便于格式化到prompt中"""
        buffer = self.get_buffer_string()
        return {
            "chat_history": f"当前摘要：{self.summary}\n\n 历史内容：{buffer}\n",
        }

    def summary_text(self, history_item: dict[str, Any]) -> str:
        """用于将旧摘要和传入的新对话生成一个新摘要"""
        history_prompt = (f"""
            你是一个强大的聊天机器人，请根据用户提供的谈话内容，总结摘要。并将其添加到先前提供的摘要中，返回一个新的摘要，除了新摘要之外的其他内容不要生成。如果用户的对话信息里有一些关键的信息，比方说姓名、爱好、性别、重要事件等等，这些内容都要全部包含在摘要中，摘要还要尽可能还原用户的对话记录。
            请不要将<example>中的内容放到摘要中，这里的数据只是一个示例数据，告诉你该如何生成新摘要
            <example>
                当前摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量。

                新的对话：
                Human：为什么你认为人工智能是一股向善的力量？
                AI：因为人工智能会帮助人类充分发挥潜力。

                新摘要：人类会问人工智能对人工智能的看法，人工智能认为人工智能是一股向善的力量，因为它将帮助人类充分发挥潜力。
            </example>
            =====================以下的数据是实际需要处理的数据=====================
            当前摘要：
                {self.summary}
            新的对话：
                human: {history_item.get('human')}
                ai: {history_item.get('ai')}
            请帮用户将上面的信息生成新摘要。
        """)
        _response = self._client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "user", "content": history_prompt}
            ],
        )

        return _response.choices[0].message.content


# 1. 创建OpenAi客户端
client = OpenAI(
    base_url=os.environ['OPENAI_BASE_URL'],
    api_key=os.environ["OPENAI_API_KEY"],
)

memory = ConversationSummaryBufferMemory(max_tokens=300, chat_histories=[], summary="")

# 2.创建一个死循环用于人机对话
while True:
    # 3.获取人类对话
    query = input("human:")

    # 4.判断下输入是否为q，如果是则退出
    if query == "q":
        break

    # 5.向openai的接口发起请求获取ai生成的内容
    memory_variables = memory.load_memory_variables()
    answer_prompt = (f"""
        你是一个强大的聊天机器人，请根据对应的上下文和用户提问解决问题。\n\n
        {memory_variables.get("chat_history")}\n\n
        用户的提问是{query}
    """)

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "user", "content": answer_prompt}
        ],
        stream=True,
    )

    # 6.循环读取流式响应的内容
    print("AI: ", flush=True, end="")
    ai_answer = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is not None:
            ai_answer += content
        print(content, flush=True, end="")
    print("")
    memory.save_context(ai_content=ai_answer, human_query=query)
