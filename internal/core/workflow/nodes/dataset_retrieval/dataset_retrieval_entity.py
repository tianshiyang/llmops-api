#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:44
@Author  : tianshiyang
@File    : dataset_retrieval_entity.py
"""
from pydantic.v1 import BaseModel

from internal.core.workflow.entities.node_entity import BaseNodeData


class RetrievalConfig(BaseModel):
    pass


class DatasetRetrievalNodeData(BaseNodeData):
    """知识库检索节点数据"""
