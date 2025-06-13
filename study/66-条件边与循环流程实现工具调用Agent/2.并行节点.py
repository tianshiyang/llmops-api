#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:34
@Author  : tianshiyang
@File    : 2.并行节点.py
"""
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState

graph_builder = StateGraph(MessagesState)


def chatbot(state: MessagesState, config: dict) -> Any:
    return {"messages": [AIMessage(content="你好，我是OpenAI开发的聊天机器人")]}


def parallel1(state: MessagesState, config: dict) -> Any:
    print("并行1: ", state)
    return {"messages": [HumanMessage(content="这是并行1函数")]}


def parallel2(state: MessagesState, config: dict) -> Any:
    print("并行2: ", state)
    return {"messages": [HumanMessage(content="这是并行2函数")]}


def chat_end(state: MessagesState, config: dict) -> Any:
    print("聊天结束: ", state)
    return {"messages": [HumanMessage(content="这是聊天结束函数")]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("parallel1", parallel1)
graph_builder.add_node("parallel2", parallel2)
graph_builder.add_node("chat_end", chat_end)

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chat_end")
graph_builder.add_edge("chatbot", "parallel1")
graph_builder.add_edge("chatbot", "parallel2")
graph_builder.add_edge("parallel2", "chat_end")

graph = graph_builder.compile()

# Mermaid 图（可以粘贴进 Mermaid 编辑器查看）
print(graph.get_graph().draw_ascii())

print(graph.invoke({"messages": [HumanMessage(content="你好，你是")]}))
