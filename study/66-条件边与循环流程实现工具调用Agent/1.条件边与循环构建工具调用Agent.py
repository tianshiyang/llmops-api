#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:34
@Author  : tianshiyang
@File    : 1.条件边与循环构建工具调用Agent.py
"""
import json
import os
from typing import TypedDict, Annotated, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import add_messages, StateGraph
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


google_serper = GoogleSerperRun(
    description="""
    一个低成本的谷歌搜索API
    当你需要获取事实信息的时候，可以调用此工具
    此工具的输入是用户查询的输入
    """,
    # args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper()
)

dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(model="dall-e-3"),
    # args_schema=DallEArgsSchema,
)

tools = [google_serper, dalle]

tool_dict = {tool.name: tool for tool in tools}

# 1.初始化大模型
llm_with_tools = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")).bind_tools(tools)


# 2.初始化state
class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# 3.添加节点
def chatbot(state: State, config: dict) -> any:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_messages = llm_with_tools.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_messages]}


def tool_executor(state: State, config: dict) -> any:
    """工具执行节点"""
    # 1.提取数据状态中的tool_calls
    tool_calls = state["messages"][-1].tool_calls
    # 2.根据找到的tool_calls去获取需要执行什么工具
    messages = []
    # 3.执行工具得到对应的结果
    for tool_call in tool_calls:
        tool = tool_dict.get(tool_call['name'])
        tool_message = ToolMessage(
            tool_call_id=tool_call['id'],
            content=json.dumps(tool.invoke(tool_call['args'])),
            nane=tool_call['name'],
        )
        messages.append(tool_message)
    return {"messages": messages}


def route(state: State, config: dict) -> Literal["tool_executor", "__end__"]:
    """通过路由来取检测下后续的返回节点是什么，返回的节点有2个，一个是工具执行，一个是结束节点"""
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"
    return "__end__"


graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tool_executor", tool_executor)

# 4.添加边
graph_builder.set_entry_point("llm")
graph_builder.add_conditional_edges("llm", route)
graph_builder.add_edge("tool_executor", "llm")

# 5.编译
graph = graph_builder.compile()
# 6.执行
state = graph.invoke({"messages": [("human", "2024年北京半程马拉松的前3名成绩是多少")]})

for message in state["messages"]:
    print("消息类型: ", message.type)
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        print("工具调用参数: ", message.tool_calls)
    print("消息内容: ", message.content)
    print("=====================================")
