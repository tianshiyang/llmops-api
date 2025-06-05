#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.6.25 PM6:28
@Author  : tianshiyang
@File    : 3.BaseTool子类创建工具.py
"""
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class MultiplyTool(BaseTool):
    name: str = "multiply_tool"
    description: str = "返回两个数相乘"
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return kwargs.get("a") * kwargs.get("b")


calculator = MultiplyTool()

# 打印下该工具的相关信息
print("名称: ", calculator.name)
print("描述: ", calculator.description)
print("参数: ", calculator.args)
print("直接返回: ", calculator.return_direct)

# 调用工具
print(calculator.invoke({"a": 2, "b": 8}))
