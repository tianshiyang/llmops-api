#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/7 23:29
@Author  : tianshiyang
@File    : 1.RunnableParallel使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

joke_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话，尽可能短一些")
poem_prompt = ChatPromptTemplate.from_template("请写一篇关于{subject}的诗，尽可能短一些")

llm = ChatOpenAI(model="moonshot-v1-8k")

parser = StrOutputParser()

joke_chain = joke_prompt | llm | parser
poem_chain = poem_prompt | llm | parser

map_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)

res = map_chain.invoke({"subject": "程序员"})

print(res)
