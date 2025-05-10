#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/7 11:46
@Author  : tianshiyang
@File    : 2.JsonOutputParser使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field

dotenv.load_dotenv()


# 1.创建一个json数据结构，用于告诉大语言模型这个json长什么样子
class Joke(BaseModel):
    joke: str = Field(description="回答用户的冷笑话")
    punchline: str = Field(description="这个冷笑话的笑点")


parser = JsonOutputParser(pydantic_object=Joke)

prompt = ChatPromptTemplate.from_template("请根据用户的提问进行回答。\n{format_instructions}\n{query}").partial(
    format_instructions=parser.get_format_instructions())

print(parser.get_format_instructions())

llm = ChatOpenAI(model="moonshot-v1-8k")

content = prompt | llm | parser

print(content.invoke({"query": "请讲一个关于程序员的冷笑话"}))
