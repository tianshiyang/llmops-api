#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/5 22:13
@Author  : tianshiyang
@File    : 3.消息提示模版拼接.py
"""
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

system_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template("你是OpenAI开发的聊天机器人，请根据用户的提问进行回复，我叫{username}")
        # ("system", '你是OpenAI开发的聊天机器人，请根据用户的提问进行回复，我叫{username}'),
    ]
)

human_prompt_template = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{query}")
    # ("human", "{query}")
])

chat_prompt = system_prompt_template + human_prompt_template

print(chat_prompt.invoke({
    "username": "张三",
    "query": "这是一个问题",
}).to_string())
