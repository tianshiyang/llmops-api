#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/16 19:53
@Author  : tianshiyang
@File    : 1.RunnableWithMessageHistory使用示例.py
"""
import dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = FileChatMessageHistory(f"chat_history_{session_id}.txt")
    return store[session_id]


prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个强大的聊天机器人，请根据用户的需求回复问题。"),
    MessagesPlaceholder("history"),
    ("human", "{query}"),
])

llm = ChatOpenAI(model="moonshot-v1-8k")

chain = prompt | llm | StrOutputParser()

with_message_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="query",
    history_messages_key="history",
)

while True:
    query = input("Human: ")

    if query == "q":
        exit(0)

    # 6.运行链并传递配置信息
    response = with_message_chain.stream(
        {"query": query},
        config={"configurable": {"session_id": "muxiaoke"}}
    )
    print("AI: ", flush=True, end="")
    for chunk in response:
        print(chunk, flush=True, end="")
    print("")
