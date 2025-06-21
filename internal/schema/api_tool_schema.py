#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.6.25 PM9:17
@Author  : tianshiyang
@File    : api_tool_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, Length, URL

from internal.schema.schema import ListField


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
