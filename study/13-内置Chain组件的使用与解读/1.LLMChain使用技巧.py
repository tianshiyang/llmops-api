#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/15 23:18
@Author  : tianshiyang
@File    : 1.LLMChain使用技巧.py
"""
import dotenv
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}主题的冷笑话")
llm = ChatOpenAI(model="moonshot-v1-8k")

chain = LLMChain(llm=llm, prompt=prompt)

# print(chain("程序员"))
# print(chain.run("程序员"))
# print(chain.apply([{"subject": "程序员"}]))
# print(chain.generate([{"subject": "程序员"}]))
# print(chain.predict(subject="程序员"))

print(chain.invoke({"subject": "程序员"}))
