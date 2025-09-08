#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:47
@Author  : tianshiyang
@File    : tool_entity.py
"""
from typing import Literal, Any

from internal.core.workflow.entities.node_entity import BaseNodeData
from pydantic import Field, field_validator

from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType


class ToolNodeData(BaseNodeData):
    """工具节点数据"""
    tool_type: Literal["builtin_tool", "api_tool", ""] = Field(alias="type")  # 工具类型
    provider_id: str  # 工具提供者id
    tool_id: str  # 工具id
    params: dict[str, Any] = Field(default_factory=dict)  # 内置工具的参数
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入变量列表
    outputs: list[VariableEntity] = Field(default_factory=lambda: [
        VariableEntity(name="text", value={"type": VariableValueType.GENERATED})
    ])  # 输出字典列表信息

    @field_validator('outputs', mode="before")
    @classmethod
    def validate_outputs(cls, outputs: list[VariableEntity]):
        return [
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED})
        ]
