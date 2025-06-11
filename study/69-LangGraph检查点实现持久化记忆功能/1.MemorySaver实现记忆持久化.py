#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 10.6.25 PM11:37
@Author  : tianshiyang
@File    : 1.MemorySaver实现记忆持久化.py
"""
import os

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
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

model = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))

checkpointer = MemorySaver()

agent = create_react_agent(tools=tools, model=model, checkpointer=checkpointer, )

# config = {"configurable": {"thread_id": 1}}

# 4.调用智能体并输出内容
print(agent.invoke(
    {"messages": [("human", "你好，我叫慕小课，我喜欢游泳打球，你喜欢什么呢?")]},
    config={"configurable": {"thread_id": 1}}
))

# 5.二次调用检测图结构程序是否存在记忆
print(agent.invoke(
    {"messages": [("human", "你知道我叫什么吗?")]},
    config={"configurable": {"thread_id": 1}}
))
