#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 19.5.25 PM10:07
@Author  : tianshiyang
@File    : 2.bind解决RunnableLambda函数多参场景.py
"""
from random import randint

from langchain_core.runnables import RunnableLambda


def get_weather(location: str, unit: str, name: str):
    """根据传入的位置+温度单位获取对应的天气信息"""
    print(f"位置{location}")
    print(f"unit {unit}")
    print(f"name {name}")
    return f"{location}天气为{randint(24, 40)}{unit}"


get_weather_runnable = RunnableLambda(get_weather).bind(unit="摄氏度", name='慕小课')

content = get_weather_runnable.invoke("广州")

print(content)
