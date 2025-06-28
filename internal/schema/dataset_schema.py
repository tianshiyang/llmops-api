#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:13
@Author  : tianshiyang
@File    : dataset_schema.py
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length, URL, Optional

from internal.model.dataset import Dataset
from pkg.paginator.paginator import PaginatorReq, PageModel


class CreateDataSetReq(FlaskForm):
    """创建知识库请求"""
    name = StringField("name", validators=[
        DataRequired("知识库名称必填"),
        Length(max=100, message="知识库名称最多100字符"),
    ])
    icon = StringField("icon", validators=[
        DataRequired("知识库图标必填"),
        URL(True)
    ])
    description = StringField("description", validators=[
        Optional(),
        Length(max=2000, message="知识库描述长度不能超过2000字符")
    ])


class GetDatasetWithPageReq(PaginatorReq):
    """获取知识库分页列表请求数据"""
    search_word = StringField("search_word", validators=[
        Optional(),
    ])


class GetDatasetsWithPageResp(Schema):
    """获取知识库分页列表响应数据"""
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }
