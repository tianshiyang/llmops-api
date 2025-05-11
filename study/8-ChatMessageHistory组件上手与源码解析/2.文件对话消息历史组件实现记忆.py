#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/11 22:39
@Author  : tianshiyang
@File    : 2.文件对话消息历史组件实现记忆.py
"""
import os

import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI(
    base_url=os.environ['OPENAI_BASE_URL'],
    api_key=os.environ["OPENAI_API_KEY"]
)

history_content = FileChatMessageHistory(file_path="./memory.txt")

while True:
    query = input("Human:")

    if query == "q":
        exit(0)

    system_prompt = (f"""
        你是openAi开发的聊天机器人，可根据响应的上下文回答用户信息，以下<context>标签中的内容是你与用户之间对话的历史内容。 \n\n
        <context>
            {history_content}
        </context>
    """)

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        stream=True
    )

    ai_content = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content is not None:
            ai_content += content
            print(content, flush=True, end="")

    history_content.add_user_message(query)
    history_content.add_ai_message(ai_content)
