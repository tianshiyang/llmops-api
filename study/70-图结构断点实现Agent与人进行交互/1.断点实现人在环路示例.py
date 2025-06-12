#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:37
@Author  : tianshiyang
@File    : 1.断点实现人在环路示例.py
"""
import os
from typing import Any, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent, ToolNode
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(model="dall-e-3"),
    args_schema=DallEArgsSchema,
)

tools = [google_serper, dalle]

llm_with_tools = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")).bind_tools(tools=tools)


def chatbot(state: MessagesState, config: dict) -> Any:
    """聊天机器人函数"""
    ai_message = llm_with_tools.invoke(state["messages"])
    return {"messages": [ai_message]}


def route(state: MessagesState, config: dict) -> Literal["tools", "__end__"]:
    """动态选择工具执行亦或者结束"""
    # 1.获取生成的最后一条消息
    ai_message = state["messages"][-1]
    # 2.检测消息是否存在tool_calls参数，如果是则执行`工具路由`
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    # 3.否则生成的内容是文本信息，则跳转到结束路由
    return "__end__"


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.set_entry_point("llm")
graph_builder.add_edge("tools", "llm")
graph_builder.add_conditional_edges("llm", route)

checkpointer = MemorySaver()

graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["tools"])

# 5.调用图架构应用
config = {"configurable": {"thread_id": 1}}
state = graph.invoke(
    {"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]},
    config=config,
)
print(state)

if hasattr(state["messages"][-1], "tool_calls") and len(state["messages"][-1].tool_calls) > 0:
    print("现在准备调用工具: ", state["messages"][-1].tool_calls)
    value = input('yes调用工具，no结束')
    if value == "yes":
        print(graph.invoke(None, config)["messages"][-1].content)
    else:
        print("图程序执行完毕")
