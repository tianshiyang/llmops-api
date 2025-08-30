#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 30.8.25 PM11:37
@Author  : tianshiyang
@File    : builtin_app_schema.py
"""

from marshmallow import Schema, fields, pre_dump

from internal.core.builtin_apps.entities.category_entity import CategoryEntity


class GetBuiltinAppCategoriesResp(Schema):
    """获取内置应用分页列表响应"""
    category = fields.String(dump_default="")
    name = fields.String(dump_default="")

    @pre_dump
    def process_data(self, data: CategoryEntity, **kwargs):
        return data.model_dump()
