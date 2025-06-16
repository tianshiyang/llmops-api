#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 14.6.25 PM6:08
@Author  : tianshiyang
@File    : 1.HumanAssistance.py
"""
import os
from typing import Any

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from pydantic import BaseModel, Field

dotenv.load_dotenv()

# 1. 定义工具
google_serper = GoogleSerperRun(
    description="这是一个低成本的谷歌搜索引擎，当你需要获取实时信息的时候，可以调用此工具",
    api_wrapper=GoogleSerperAPIWrapper()
)


class HumanAssistanceArgs(BaseModel):
    query: str = Field(description="问题的输入")


@tool(description="向人类获取帮助", args_schema=HumanAssistanceArgs)
def human_assistance(query: str) -> Any:
    """向人类请求帮助"""
    human_response = interrupt({"query": query})
    print(human_response, '-------')
    return human_response["data"]


tools = [google_serper, human_assistance]

# 定义图
graph_builder = StateGraph(MessagesState)

# 初始化大模型
llm_with_tools = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0).bind_tools(tools=tools)


# 定义节点函数
def chatbot(state: MessagesState, config: dict) -> Any:
    ai_message = llm_with_tools.invoke(state["messages"])
    assert (len(ai_message.tool_calls) <= 1)
    return {"messages": ai_message}


tool_node = ToolNode(tools=tools)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)

user_input = "我需要一些专家的指导来建立一个人工智能代理。你能帮我请求帮助吗？"
config = {"configurable": {"thread_id": "1"}}

human_response = (
    "我们，专家在这里提供帮助！我们建议您使用LangGraph来构建代理。"
    "它比简单的自治代理更加可靠和可扩展。"
)

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
