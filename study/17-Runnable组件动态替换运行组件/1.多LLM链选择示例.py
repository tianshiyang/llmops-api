#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:10
@Author  : tianshiyang
@File    : 1.多LLM链选择示例.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = PromptTemplate.from_template("{query}")
llm = ChatOpenAI(model="moonshot-v1-8k").configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="moonshot-v1-8k",
    gpt4=ChatOpenAI(model="gpt-4o"),
)

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并传递配置信息，并切换到文心一言模型或者gpt4模型
content = chain.with_config(
    configurable={
        "llm": "moonshot-v1-8k"
    }
).invoke(
    {"query": "你好，你是什么模型呢?"}
)
print(content)
