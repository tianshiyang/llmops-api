#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/15 23:23
@Author  : tianshiyang
@File    : 2.LCEL文档填充链.py
"""
import dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

llm = ChatOpenAI(model="moonshot-v1-8k")

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个强大的聊天机器人，能根据用户提供的上下文来回复用户的问题。\n\n<context>{context}</context>"),
    ("human", "{query}")
])

chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

documents = [
    Document(page_content="小明喜欢绿色，但不喜欢黄色"),
    Document(page_content="小王喜欢粉色，也有一点喜欢红色"),
    Document(page_content="小泽喜欢蓝色，但更喜欢青色"),
]

content = chain.invoke({
    "query": "请帮我统计一下大家都喜欢什么颜色",
    "context": documents,
})
print(content)
