#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 18.6.25 PM10:06
@Author  : tianshiyang
@File    : tool_entity.py
"""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """工具参数类型枚举类"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class ToolParams(BaseModel):
    name: str  # 参数的实际名字
    label: str  # 参数的展示标签
    type: ToolType  # 参数的类型
    required: bool = False  # 是否必填
    default: Any | None = None
    min: float | None = None
    max: float | None = None
    options: list[dict[str, Any]] = Field(default_factory=list)


class ToolEntity(BaseModel):
    name: str  # 工具名字
    label: str  # 工具标签
    description: str  # 工具描述
    params: list[ToolParams] = Field(default_factory=list)  # 工具的参数信息
