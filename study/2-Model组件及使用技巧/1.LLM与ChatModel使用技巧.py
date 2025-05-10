#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/6 22:51
@Author  : tianshiyang
@File    : 1.LLM与ChatModel使用技巧.py
"""

import dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from datetime import datetime

dotenv.load_dotenv()

# 1. 编排prompt
chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    HumanMessagePromptTemplate.from_template("{query}")
]).partial(now=datetime.now())

# 2. 创建语言大模型
llm = ChatOpenAI(model="moonshot-v1-8k")
ai_message = llm.invoke(chat_prompt_template.invoke({
    "query": "现在是几点，请讲一个程序员的冷笑话"
}))

print(ai_message.type)
print(ai_message.content)
print(ai_message.response_metadata)
