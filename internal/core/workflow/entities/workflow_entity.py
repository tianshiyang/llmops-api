#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:37
@Author  : tianshiyang
@File    : workflow_entity.py
"""
from typing import TypedDict, Annotated, Any

from internal.core.workflow.entities.node_entity import NodeResult


def _process_dict(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """工作流状态字典归纳函数"""
    # 1.处理left和right出现空的情况
    left = left or {}
    right = right or {}
    return {**left, **right}


def _process_node_result(left: dict[str, Any], right: dict[str, Any]) -> list[NodeResult]:
    """工作流状态节点结果列表归纳函数"""
    # 1.处理left和right出现空的情况
    left = left or []
    right = right or []

    # 2.合并列表更新后返回
    return left + right


class WorkflowState(TypedDict):
    """工作流图程序状态字典"""
    inputs: Annotated[dict[str, Any], _process_dict]  # 工作流的最初始输入，也就是工具的输入
    outputs: Annotated[dict[str, Any], _process_dict]  # 工作流的最终输出结果，也就是工具输出
    node_results: Annotated[list[NodeResult], _process_node_result]  # 各节点的运行结果
