#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:44
@Author  : tianshiyang
@File    : dataset_retrieval_entity.py
"""
from pydantic import BaseModel, Field, validator, field_validator
from uuid import UUID
from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity, VariableValueType, VariableType
from internal.exception import FailException


class RetrievalConfig(BaseModel):
    pass


class DatasetRetrievalNodeData(BaseNodeData):
    """知识库检索节点数据"""
    dataset_ids: list[UUID]  # 关联的知识库列表
    retrieval_config: RetrievalConfig = Field(default_factory=list)  # 检索配置
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入变量信息
    outputs: list[VariableEntity] = Field(default_factory=lambda: [
        VariableEntity(name="combine_documents", value={"type": VariableValueType.GENERATED})
    ])

    @field_validator("outputs", mode="before")
    @classmethod
    def validate_outputs(cls, value: list[VariableEntity]):
        return [
            VariableEntity(name="combine_documents", value={"type": VariableValueType.GENERATED})
        ]

    @field_validator("inputs")
    @classmethod
    def validate_inputs(cls, value: list[VariableEntity]):
        """校验输入变量信息"""
        # 1.判断是否只有一个输入变量，如果有多个则抛出错误
        if len(value) != 1:
            raise FailException("知识库节点输入变量信息出错")

        # 2.判断输入遍历那个的类型及字段名称是否出错
        query_input = value[0]
        if query_input.name != "query" or query_input.type != VariableType.STRING or query_input.required is False:
            raise FailException("知识库节点输入变量名字/变量类型/必填属性出错")

        return value
