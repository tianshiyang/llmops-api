#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:36
@Author  : tianshiyang
@File    : 1.删除与更新消息示例.py
"""
import os
from typing import Any

import dotenv
from langchain_core.messages import RemoveMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph

dotenv.load_dotenv()

llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))


def chatbot(state: MessagesState, config: dict) -> Any:
    print(state["messages"])
    return {"messages": [llm.invoke(state["messages"])]}


def delete_human_message(state: MessagesState, config: dict) -> Any:
    human_message = state['messages'][0]
    return {"messages": [RemoveMessage(id=human_message.id)]}


def update_ai_message(state: MessagesState, config: dict) -> Any:
    message = state["messages"][-1]
    return {"message": [AIMessage(id=message.id, content="这是修改后的内容" + message.content)]}


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("delete_human_message", delete_human_message)
graph_builder.add_node("update_ai_message", update_ai_message)

graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", "delete_human_message")
graph_builder.add_edge("delete_human_message", "update_ai_message")
graph_builder.set_finish_point("update_ai_message")

graph = graph_builder.compile()

print(graph.invoke({"messages": [("human", "你好，你是")]}))
