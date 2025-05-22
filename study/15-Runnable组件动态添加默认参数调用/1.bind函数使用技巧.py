#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:06
@Author  : tianshiyang
@File    : 1.bind函数使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}")
])

llm = ChatOpenAI()

chain = prompt | llm.bind(model="qwen-long") | StrOutputParser()

content = chain.invoke({
    "query": "你是什么模型呢,具体哪个版本呢"
})

print(content)
