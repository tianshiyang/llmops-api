#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/6 22:51
@Author  : tianshiyang
@File    : 3.Model流式输出.py
"""
import dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    HumanMessagePromptTemplate.from_template("{query}")
]).partial(now=datetime.now())

llm = ChatOpenAI(model="moonshot-v1-8k")
ai_messages = llm.stream(prompt.invoke({
    "query": "现在是几点，请讲一个程序员的冷笑话"
}))

for ai_message in ai_messages:
    print(ai_message.content, flush=True, end="")
