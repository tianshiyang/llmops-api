#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM2:56
@Author  : tianshiyang
@File    : 2.基于逻辑和语义的路由分发.py
"""
import os

import dotenv
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class RouteQuery(BaseModel):
    datasource: Literal["python_docs", "javascript_docs", "golang_docs"] = Field(
        description="请根据用户的输入，判断使用的那个文档"
    )


def choose_route(route: RouteQuery):
    if route.datasource == "python_docs":
        return 'python'
    elif route.datasource == "javascript_docs":
        return 'javascript'
    else:
        return 'go'


structured_llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")).with_structured_output(RouteQuery)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个擅长将用户问题路由到适当的数据源的专家。\n请根据问题涉及的编程语言，将其路由到相关数据源"),
    ("human", "{question}")
])

chain = {
            "question": RunnablePassthrough()
        } | prompt | structured_llm | choose_route

question = """为什么下面的代码不工作了，请帮我检查下：

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(["human", "speak in {language}"])
prompt.invoke("中文")"""

print(chain.invoke(question))
