#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM6:27
@Author  : tianshiyang
@File    : 2.StructuredTool类方法创建工具.py
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


def multiply(a: int, b: int):
    return a * b


async def amultiply(a: int, b: int):
    return a * b


calculator = StructuredTool.from_function(
    func=multiply,
    name="multiply_tool",
    description="两个数字相乘",
    return_direct=True,
    coroutine=amultiply,
    args_schema=MultiplyInput,
)

print(calculator.name)
print(calculator.description)
print(calculator.args)
print(calculator.return_direct)
