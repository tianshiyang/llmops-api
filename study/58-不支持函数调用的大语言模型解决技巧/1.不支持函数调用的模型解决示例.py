#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM8:46
@Author  : tianshiyang
@File    : 1.不支持函数调用的模型解决示例.py
"""
import json
import os
from operator import itemgetter
from typing import Any, Type

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from langchain_core.tools import BaseTool, render_text_description_and_args
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type, Any, TypedDict, Dict, Optional

dotenv.load_dotenv()

base_url = "https://restapi.amap.com/v3"


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="用户的输入内容，作用于搜索")


class GaoDeWeatherArgsSchema(BaseModel):
    query: str = Field(description="用户输入的输入内容，用于查询天气信息，例如北京")


class GaodeWeaherTool(BaseTool):
    name: str = "gaode_weather_tool"
    description: str = "查询用户输入城市的天气信息"
    args_schema: Type[BaseModel] = GaoDeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        api_key = os.getenv("gaode_api_key")
        if not api_key:
            return "没有高德地图的的api key"
        city = kwargs.get("city")
        if not city:
            return "没有输入的城市信息"
        session = requests.session()
        res = session.request(
            method="GET",
            url=f"{base_url}/config/district",
            params={
                "key": api_key,
                "keywords": city,
                "subdistrict": 0
            }
        ).json()
        if res.get("info") != "OK":
            return "获取城市编码失败"
        else:
            adcode = res.districts[0].adcode
            weather_info = session.request(
                method="GET",
                url=f"{base_url}/weather/weatherInfo?parameters",
                params={
                    "key": api_key,
                    "city": adcode,
                }
            ).json()
            if weather_info.get("info") != "OK":
                return "获取天气信息失败"
            else:
                return json.dumps(weather_info)


gaode_weather = GaodeWeaherTool()
google_serper = GoogleSerperRun(
    name="google_serper_tool",
    description="这是一个低成本的调用谷歌搜索获取用户输入结果的工具",
    api_wrapper=GoogleSerperAPIWrapper()
)

tool_dict = {
    gaode_weather.name: gaode_weather,
    google_serper.name: google_serper
}

tools = [tool for tool in tool_dict.values()]


class ToolCallRequest(BaseModel):
    name: str = Field(description="函数调用的名称")
    arguments: str = Field(description="函数调用的参数，是一个字典")


def invoke_tool(tool_call_result: ToolCallRequest, config: Optional[RunnableConfig] = None) -> str:
    print(config)
    tool = tool_dict[tool_call_result.get("name")]
    tool_arguments = tool_call_result.get("arguments")
    return tool.invoke(tool_arguments, config=config)


system_prompt = """你是一个由OpenAI开发的聊天机器人，可以访问以下工具。
以下是每个工具的名称和描述：

{rendered_tools}

根据用户输入，返回要使用的工具的名称和输入。
将您的响应作为具有`name`和`arguments`键的JSON块返回。
`arguments`应该是一个字典，其中键对应于参数名称，值对应于请求的值。"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{query}")
]).partial(rendered_tools=render_text_description_and_args(tools))

llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))

chain = prompt | llm | JsonOutputParser() | RunnablePassthrough.assign(content=invoke_tool) | itemgetter("content")

result = chain.invoke({"query": "马拉松的世界记录是多少"})
print(result)
# prompt.invoke()
