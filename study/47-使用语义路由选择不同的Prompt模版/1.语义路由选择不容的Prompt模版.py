#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM3:54
@Author  : tianshiyang
@File    : 1.语义路由选择不容的Prompt模版.py
"""
import os

from typing import Literal
from langchain_community.utils.math import cosine_similarity
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from custom_embeddings import DashScopeEmbeddings

# 1.定义两份不同的prompt模板(物理模板、数学模板)
physics_template = """你是一位非常聪明的物理教程。
你擅长以简洁易懂的方式回答物理问题。
当你不知道问题的答案时，你会坦率承认自己不知道。

这是一个问题：
{query}"""
math_template = """你是一位非常优秀的数学家。你擅长回答数学问题。
你之所以如此优秀，是因为你能将复杂的问题分解成多个小步骤。
并且回答这些小步骤，然后将它们整合在一起回来更广泛的问题。

这是一个问题：
{query}"""

embedding = DashScopeEmbeddings()

prompt_templates = [physics_template, math_template]

prompt_embeddings = embedding.embed_documents(prompt_templates)

print(prompt_embeddings, 'prompt_embedding')


class RouteQuery(BaseModel):
    datasource: Literal['数学', '物理'] = Field(
        description="请根据用户的输入，判断它属于哪一门课程"
    )

    # 实现方式1
    # def prompt_router(input) -> ChatPromptTemplate:
    """根据传递的query计算返回不同的提示模板"""
    # query_embedding = embedding.embed_query(input['query'])
    #
    # # 计算相似性
    # similarity = cosine_similarity(prompt_embeddings, [query_embedding])[0]
    #
    # most_similar = prompt_templates[similarity.argmax()]
    #
    # print("使用数学模板" if most_similar == math_template else "使用物理模板")
    #
    # return ChatPromptTemplate.from_template(most_similar)


# 实现方式2
def prompt_router(input) -> ChatPromptTemplate:
    structured_llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")).with_structured_output(RouteQuery)
    res = structured_llm.invoke(input['query']).datasource
    print(res)
    if res == '数学':
        return ChatPromptTemplate.from_template(math_template)
    else:
        return ChatPromptTemplate.from_template(physics_template)


chain = {
            "query": RunnablePassthrough()
        } | RunnableLambda(prompt_router) | ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")) | StrOutputParser()

print(chain.invoke("黑洞是什么?"))
print("======================")
print(chain.invoke("能介绍下余弦计算公式么？"))
