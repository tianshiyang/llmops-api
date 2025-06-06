#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM6:29
@Author  : tianshiyang
@File    : gaode_weather_tool.py
"""
import json
import os
from typing import Any, Type

import dotenv
import requests
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel

dotenv.load_dotenv()
request_base_url: str = "https://restapi.amap.com/v3"


class GaoDeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询的城市信息，如北京")


class GaoDeWeatherTool(BaseTool):
    name: str = "gaode_weather_tool"
    description: str = "通过城市获取天气信息"
    args_schema: Type[BaseModel] = GaoDeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        try:
            city = kwargs.get("city")
            api_key = os.getenv("GAODE_API_KEY")
            if not api_key:
                return f"没有配置高德api信息"
            session = requests.session()
            city_response = session.request(
                method="GET",
                url=f"{request_base_url}/config/district",
                params={"keywords": city, "key": api_key, "subdistrict": 0},
            )

            city_data = city_response.json()

            if city_data.get("info") == "OK":
                adcode = city_data.get("districts")[0].get("adcode")

                weather_response = session.request(
                    method="GET",
                    url=f"{request_base_url}/weather/weatherInfo",
                    params={"city": adcode, "key": api_key, },
                )
                weather_data = weather_response.json()
                if weather_data.get("info") == "OK":
                    return json.dumps(weather_data)
                else:
                    return "获取高德天气失败"
            else:
                return f"获取省市区编码失败"
        except Exception as e:
            return f"获取天气失败"


gaode_weather = GaoDeWeatherTool()
print(gaode_weather.invoke({"city": "北京"}))
