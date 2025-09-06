#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:45
@Author  : tianshiyang
@File    : end_entity.py
"""
from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity
from pydantic.v1 import Field


class EndNodeData(BaseNodeData):
    """结束节点数据"""
    outputs: list[VariableEntity] = Field(default_factory=list)  # 结束节点需要输出的数据
