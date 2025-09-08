#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:45
@Author  : tianshiyang
@File    : dataset_retrieval_node.py
"""
import time
from typing import Any, Optional

from flask import Flask
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr
from uuid import UUID

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.dataset_retrieval.dataset_retrieval_entity import DatasetRetrievalNodeData
from internal.core.workflow.uitls.helper import extract_variables_from_state


class DatasetRetrievalNode(BaseNode):
    """知识库检索节点"""

    node_data: DatasetRetrievalNodeData
    _retrieval_tool: BaseTool = PrivateAttr(None)

    def __init__(
            self,
            *args: Any,
            flask_app: Flask,
            account_id: UUID,
            **kwargs: Any
    ):
        """构造函数，完成知识库检索节点的初始化"""
        # 1.调用父类构造函数完成数据初始化
        super().__init__(*args, **kwargs)

        # 2.导入依赖注入及检索服务
        from app.http.moudle import injector
        from internal.service.retrieval_service import RetrievalService

        retrieval_service = injector.get(RetrievalService)

        # 3.构建检索服务
        self._retrieval_tool = retrieval_service.create_langchain_tool_from_search(
            flask_app=flask_app,
            dataset_ids=self.node_data.dataset_ids,
            account_id=account_id,
            **self.node_data.retrieval_config.dict()
        )

    def invoke(self, state: WorkflowState, config: Optional[RunnableConfig] = None, **kwargs: Any) -> WorkflowState:
        """知识库检索节点调用函数，执行响应的知识库检索后返回"""
        # 1.提取节点的输入变量字典映射
        start_at = time.perf_counter()
        inputs_dict = extract_variables_from_state(self.node_data.inputs, state)

        # 2.调用知识库检索工具
        combine_document = self._retrieval_tool.invoke(inputs_dict)

        # 3.提取并构建输出数据结构
        outputs = {}
        if self.node_data.outputs:
            outputs[self.node_data.outputs[0].name] = combine_document
        else:
            outputs["combine_documents"] = combine_document

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCEEDED,
                    inputs=inputs_dict,
                    outputs=outputs,
                    latency=(time.perf_counter() - start_at),
                )
            ]
        }
