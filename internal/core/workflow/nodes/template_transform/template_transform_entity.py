#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:47
@Author  : tianshiyang
@File    : template_transform_entity.py
"""
from pydantic import Field, validator, field_validator

from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType


class TemplateTransformNodeData(BaseNodeData):
    """模板转换节点数据"""
    template: str = ""  # 需要拼接转换的字符串模版
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入列表信息
    outputs: list[VariableEntity] = Field(default_factory=lambda: [
        VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
    ])

    @field_validator("outputs", mode="before")
    @classmethod
    def validate_outputs(cls, outputs: list[VariableEntity]):
        return [
            VariableEntity(name="output", value={"type": VariableValueType.GENERATED})
        ]
