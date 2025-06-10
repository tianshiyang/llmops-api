#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 7.6.25 PM9:02
@Author  : tianshiyang
@File    : 1.基础LangGraph示例.py
"""
import os
from typing import TypedDict, Annotated

import dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

dotenv.load_dotenv()

# 1. 定义大语言模型
llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))


# 2. 初始状态
class State(TypedDict):
    """图结构的数据状态"""
    messages: Annotated[list, add_messages]
    use_name: str


graph_builder = StateGraph(State)


# 3. 定义节点
def chatbot(state: State, config: dict) -> any:
    """聊天机器人节点，使用大语言模型根据传递的消息列表生成内容"""
    ai_message = llm.invoke(state["messages"])
    return {"messages": ai_message, "use_name": "chatbot"}


graph_builder.add_node("llm", chatbot)

# 4. 定义节点连接的边

graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

# 5.编译
graph = graph_builder.compile()

# 6.运行
result = graph.invoke({"messages": [("human", "你好，你是谁，我叫慕小课，我喜欢打篮球游泳")], "use_name": "graph"})

print(result)
