#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:45
@Author  : tianshiyang
@File    : end_node.py
"""
from typing import Optional

from pydantic.v1 import BaseModel
from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes.end.end_entity import EndNodeData
import time

from internal.core.workflow.uitls.helper import extract_variables_from_state


class EndNode(BaseModel):
    """结束节点"""
    node_data: EndNodeData

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None) -> WorkflowState:
        # 1.提取节点中需要输出的数据
        start_at = time.perf_counter()
        outputs_dict = extract_variables_from_state(self.node_data.outputs, state)

        # 2.组装状态并返回
        return {
            "outputs": outputs_dict,
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs={},
                    outputs=outputs_dict,
                    latency=(time.perf_counter() - start_at)
                )
            ]
        }
