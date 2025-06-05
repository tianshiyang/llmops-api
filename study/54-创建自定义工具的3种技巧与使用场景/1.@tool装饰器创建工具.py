#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM6:27
@Author  : tianshiyang
@File    : 1.@tool装饰器创建工具.py
"""
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="这是第一个数字")
    b: int = Field(description="这是第二个数字")


@tool("multiply_tool", args_schema=MultiplyInput, description="两个数字相乘", return_direct=True)
def multiply(a: int, b: int):
    """将传递的两个数字相乘"""
    return a * b


# 打印函数相关信息
print("函数名称:", multiply.name)
print("函数描述：", multiply.description)
print("参数：", multiply.args)
print("是否立即返回", multiply.return_direct)

# 调用工具
result = multiply.invoke({
    "a": 2,
    "b": 3
})

print(result)
