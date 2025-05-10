#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/6 22:51
@Author  : tianshiyang
@File    : 2.Model批处理.py
"""
import dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from datetime import datetime

from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    HumanMessagePromptTemplate.from_template("{query}")
]).partial(now=datetime.now())

llm = ChatOpenAI(model="moonshot-v1-8k")
ai_messages = llm.batch([
    prompt.invoke({"query": "你好，你是?"}),
    prompt.invoke({"query": "请讲一个关于程序员的冷笑话"}),
])

for message in ai_messages:
    print(message.content)
    print("------")
