#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:09
@Author  : tianshiyang
@File    : 1.configurable_fields使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = PromptTemplate.from_template("请生成一个小于{x}的整数")

llm = ChatOpenAI(model="moonshot-v1-8k").configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="大语言模型的温度",
        description="温度越低，大语言模型生成的内容越确定，温度越高，生成内容越随机"
    )
)

chain = prompt | llm | StrOutputParser()

content = chain.invoke({
    "x": 1000
})

print(content)

print("========")

with_config_chain = chain.with_config(configurable={
    "llm_temperature": 0
})

content2 = with_config_chain.invoke({
    "x": 1000
})

print(content2)
