#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.9.25 PM9:45
@Author  : tianshiyang
@File    : http_request_entity.py
"""
from enum import Enum
from typing import Optional

from internal.core.workflow.entities.node_entity import BaseNodeData
from pydantic import HttpUrl, validator, Field, field_validator

from internal.core.workflow.entities.variable_entity import VariableEntity, VariableType, VariableValueType
from internal.exception import ValidateErrorException


class HttpRequestMethod(str, Enum):
    """HTTP请求方法类型枚举"""
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"


class HttpRequestInputType(str, Enum):
    """Http请求输入变量类型"""
    PARAMS = "params"  # query参数
    HEADERS = "headers"  # header请求头
    BODY = "body"  # body参数


class HttpRequestNodeData(BaseNodeData):
    """HTTP请求节点数据"""
    url: Optional[HttpUrl] = None  # 请求URL低脂
    method: HttpRequestMethod = HttpRequestMethod.GET  # API请求方法
    inputs: list[VariableEntity] = Field(default_factory=list)  # 输入变量列表
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(
                name="status_code",
                type=VariableType.INT,
                value={"type": VariableValueType.GENERATED, "content": 0},
            ),
            VariableEntity(name="text", type={"type": VariableValueType.GENERATED}),
        ]
    )

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, url: Optional[HttpUrl]):
        return url if url != "" else None

    @field_validator("outputs", mode="before")
    @classmethod
    def validate_outputs(cls, outputs: list[VariableEntity]):
        return [
            VariableEntity(
                name="status_code",
                type=VariableType.INT,
                value={"type": VariableValueType.GENERATED, "content": 0},
            ),
            VariableEntity(name="text", value={"type": VariableValueType.GENERATED}),
        ]

    @field_validator("inputs")
    @classmethod
    def validate_inputs(cls, inputs: list[VariableEntity]):
        """校验输入列表数据"""
        # 1.校验判断输入变脸列表中的类型信息
        for input in inputs:
            if input.meta.get("type") not in HttpRequestInputType.__members__.values():
                raise ValidateErrorException("Http请求参数结构错误")

        return inputs
