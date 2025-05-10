#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/7 23:29
@Author  : tianshiyang
@File    : 2.RunnableParallel模拟检索.py
"""
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


def retrieval(query: str) -> str:
    """一个模拟的检索器函数"""
    print("正在检索:", query)
    return "我是慕小课"


prompt = ChatPromptTemplate.from_template("""请根据用户的问题回答，可以参考对应的上下文进行生成。

<context>
{context}
</context>

用户的提问是: {query}
""")

llm = ChatOpenAI(model="moonshot-v1-8k")

parser = StrOutputParser()

chain = {
            "context": lambda x: retrieval(x["query"]),
            "query": itemgetter("query"),
        } | prompt | llm | parser

res = chain.invoke({
    "query": "我是谁"
})

print(res)
