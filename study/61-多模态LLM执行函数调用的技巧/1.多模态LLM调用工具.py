#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 7.6.25 PM8:58
@Author  : tianshiyang
@File    : 1.多模态LLM调用工具.py
"""
import base64
import json
import os
from typing import Type, Any

import dotenv
import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如：广州")


class GaodeWeatherTool(BaseTool):
    """根据传入的城市名查询天气"""
    name: str = "gaode_weather"
    description: str = "当你想询问天气或与天气相关的问题时的工具。"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """运行工具获取对应城市的天气预报"""
        try:
            # 1.获取高德API秘钥，如果没有则抛出错误
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"高德开放平台API秘钥未配置"

            # 2.提取传递的城市名字并查询行政编码
            city = kwargs.get("city", "")
            session = requests.session()
            api_domain = "https://restapi.amap.com/v3"
            city_response = session.request(
                method="GET",
                url=f"{api_domain}/config/district?keywords={city}&subdistrict=0&extensions=all&key={gaode_api_key}",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()
            city_data = city_response.json()

            # 3.提取行政编码调用天气预报查询接口
            if city_data.get("info") == "OK":
                if len(city_data.get("districts")) > 0:
                    ad_code = city_data["districts"][0]["adcode"]

                    weather_response = session.request(
                        method="GET",
                        url=f"{api_domain}/weather/weatherInfo?city={ad_code}&extensions=all&key={gaode_api_key}&output=json",
                        headers={"Content-Type": "application/json; charset=utf-8"},
                    )
                    weather_response.raise_for_status()
                    weather_data = weather_response.json()
                    if weather_data.get("info") == "OK":
                        return json.dumps(weather_data)

            session.close()
            return f"获取{kwargs.get('city')}天气预报信息失败"
            # 4.整合天气预报信息并返回
        except Exception as e:
            return f"获取{kwargs.get('city')}天气预报信息失败"


# 构建提示词模版
prompt = ChatPromptTemplate.from_messages([
    ("human", [
        {"type": "text", "text": "请获取下上传图片所在城市的天气预报。"},
        {"type": "image_url", "image_url": {"url": "{image_url}"}}
    ])
])
weather_prompt = ChatPromptTemplate.from_template("""
请整理天气预报的信息，并转化成对用户友好的输出
<weather>
{weather}
</weather>
""")

# 创建LLM并绑定工具
llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"))
llm_with_tools = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL")).bind_tools(tools=[GaodeWeatherTool()],
                                                                           tool_choice="gaode_weather")

chain = {
            "image_url": RunnablePassthrough(),
        } | prompt | llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | GaodeWeatherTool()

result_chain = {
                   "weather": RunnablePassthrough()
               } | weather_prompt | llm | StrOutputParser()


def image_url_to_base64(url: str) -> str:
    """
    下载图片并将其编码为 base64 字符串，返回 data URI 格式，可直接用于 OpenAI 的 image_url。
    """
    response = requests.get(url)
    response.raise_for_status()  # 如果下载失败则抛出异常

    # 获取图片的 MIME 类型
    content_type = response.headers.get("Content-Type", "image/jpeg")

    # 编码成 base64
    base64_data = base64.b64encode(response.content).decode("utf-8")

    # 拼接成 OpenAI 兼容的格式
    return f"data:{content_type};base64,{base64_data}"


weather_result = chain.invoke(
    image_url_to_base64("http://alpha-dev.oss-cn-beijing.aliyuncs.com/alpha_sales/guangzhou.jpg"))

print(weather_result)

print(result_chain.invoke(weather_result))
