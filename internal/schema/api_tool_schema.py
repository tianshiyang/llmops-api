#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.6.25 PM9:17
@Author  : tianshiyang
@File    : api_tool_schema.py
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, Length, URL, Optional

from internal.model import ApiToolProvider
from internal.schema.schema import ListField
from pkg.paginator.paginator import PaginatorReq


class CreateApiToolReq(FlaskForm):
    """创建自定义API工具请求"""
    name: str = StringField("name", validators=[
        DataRequired(message="工具提供者名字不能为空"),
        Length(min=1, max=30, message="工具提供者的名字长度在1-30")
    ])

    icon: str = StringField("icon", validators=[
        DataRequired(message="工具提供者的图标不能为空"),
        URL(message="工具提供者的图标必须是URL链接")
    ])

    openapi_schema: str = StringField("openapi_schema", validators=[
        DataRequired(message="openapi_schema字符串不能为空")
    ])
    headers: list = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        """校验headers请求的数据是否正确，涵盖列表校验，列表元素校验"""
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidationError("headers里的每一个元素都必须是字典")
            if set(header.keys()) != {"key", "value"}:
                raise ValidationError("headers里的每一个元素都必须包含key/value两个属性，不允许有其他属性")


class GetApiToolProvidersWithPageReq(PaginatorReq):
    search_word: str = StringField("search_word", validators=[
        Optional()
    ])


class GetApiToolProvidersWithPageResp(Schema):
    """获取API工具提供者分页列表数据响应"""
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    headers = fields.List(fields.Dict, default=[])
    tools = fields.List(fields.Dict, default=[])
    created_at = fields.Integer(default=0)

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        tools = data.tools
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "headers": data.headers,
            "tools": [{
                "id": tool.id,
                "description": tool.description,
                "name": tool.name,
                "inputs": [{k: v for k, v in parameter.items() if k != "in"} for parameter in tool.parameters]
            } for tool in tools],
            "created_at": int(data.created_at.timestamp())
        }


class GetApiToolProviderResp(Schema):
    id: str = fields.UUID()
    name: str = fields.String()
    icon: str = fields.String()
    openapi_schema: str = fields.String()
    headers: list = fields.List(fields.Dict, default=[])
    created_at = fields.Integer(default=0)

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "openapi_schema": data.openapi_schema,
            "headers": data.headers,
            "created_at": int(data.created_at.timestamp())
        }


class GetApiToolResp(Schema):
    id: str = fields.UUID()
    name: str = fields.String()
    description: str = fields.String()
    inputs: list = fields.List(fields.Dict, default=[])
    provider: dict = fields.Dict()

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        provider = data.provider
        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            "inputs": [{k: v for k, v in parameter.items() if k != "in"} for parameter in data.parameters],
            "provider": {
                "id": provider.id,
                "name": provider.name,
                "icon": provider.icon,
                "description": provider.description,
                "headers": provider.headers,
            }
        }


class GetAPIToolProviderById(FlaskForm):
    provider_id = StringField("provider_id", validators=[
        DataRequired(message="provider_id必填")
    ])
