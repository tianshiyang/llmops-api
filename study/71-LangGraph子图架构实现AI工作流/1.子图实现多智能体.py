#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:38
@Author  : tianshiyang
@File    : 1.子图实现多智能体.py
"""
import os
from typing import TypedDict, Annotated, Any

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

dotenv.load_dotenv()

google_serper = GoogleSerperRun(
    api_wrapper=GoogleSerperAPIWrapper()
)


# 合并策略
def reduce_str(old: str | None, new: str | None) -> str:
    print(old, new)
    if new is not None and new != "":
        return new
    return old


class AgentState(TypedDict):
    query: Annotated[str, reduce_str]  # 原始问题
    xhs_content: Annotated[str, reduce_str]  # 小红书文案
    live_content: Annotated[str, reduce_str]  # 直播文案


class LiveAgentState(MessagesState):
    """直播文案智能体状态"""
    query: Annotated[str, reduce_str]
    live_content: Annotated[str, reduce_str]
    xhs_content: Annotated[str, reduce_str]
    pass


llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))


def live_chatbot(state: LiveAgentState, config: dict) -> Any:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个拥有10年经验的直播文案专家，请根据用户提供的产品整理一篇直播带货脚本文案，如果在你的知识库内找不到关于该产品的信息，可以使用搜索工具。"),
        ("human", "{query}"),
        ("placeholder", "{chat_history}")
    ])
    chain = prompt | llm.bind_tools([google_serper])
    print(state, 'state')
    ai_message = chain.invoke({"query": state["query"], "chat_history": state["messages"]})
    return {
        "messages": [ai_message],
        "live_content": ai_message.content
    }


live_graph = StateGraph(LiveAgentState)

live_graph.add_node("live_chatbot", live_chatbot)
live_graph.add_node("tools", ToolNode([google_serper]))

live_graph.set_entry_point("live_chatbot")
live_graph.add_conditional_edges("live_chatbot", tools_condition)
live_graph.add_edge("tools", "live_chatbot")


class XHSAgentState(AgentState):
    # 小红书智能体
    pass


def xhs_chatbot(state: XHSAgentState, config: dict) -> Any:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个小红书文案大师，请根据用户传递的商品名，生成一篇关于该商品的小红书笔记文案，注意风格活泼，多使用emoji表情。"),
        ("human", "{query}"),
    ])
    chain = prompt | llm | StrOutputParser()

    # 2.调用链并生成内容更新状态
    return {"xhs_content": chain.invoke({"query": state["query"]})}


xhs_graph = StateGraph(XHSAgentState)

xhs_graph.add_node("xhs_chatbot", xhs_chatbot)
xhs_graph.set_entry_point("xhs_chatbot")
xhs_graph.set_finish_point("xhs_chatbot")


# 3.创建入口图并添加节点、边
def parallel_node(state: AgentState, config: RunnableConfig) -> Any:
    return state


state_graph = StateGraph(AgentState)
state_graph.add_node("parallel_node", parallel_node)
state_graph.add_node("live_agent", live_graph.compile())
state_graph.add_node("xhs_agent", xhs_graph.compile())

state_graph.set_entry_point("parallel_node")
state_graph.add_edge("parallel_node", "live_agent")
state_graph.add_edge("parallel_node", "xhs_agent")
state_graph.set_finish_point("live_agent")
state_graph.set_finish_point("xhs_agent")

# 4.编译入口图
agent = state_graph.compile()

# 5.执行入口图并打印结果
print(agent.invoke({"query": "潮汕牛肉丸"}))
