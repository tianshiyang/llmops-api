#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:13
@Author  : tianshiyang
@File    : dataset_schema.py
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length, URL, Optional, AnyOf, NumberRange

from internal.entity.dataset_entity import RetrievalStrategy
from internal.lib.helper import datetime_to_timestamp
from internal.model.dataset import Dataset, DatasetQuery
from pkg.paginator.paginator import PaginatorReq


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


class GetDatasetResp(Schema):
    """获取知识库详情响应结构"""
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
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
            "hit_count": data.hit_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


class UpdateDatasetReq(FlaskForm):
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


class GetDatasetQueriesResp(Schema):
    """获取知识库最近查询响应结构"""
    id = fields.UUID(dump_default="")
    dataset_id = fields.UUID(dump_default="")
    query = fields.String(dump_default="")
    source = fields.String(dump_default="")
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: DatasetQuery, **kwargs):
        return {
            "id": data.id,
            "dataset_id": data.dataset_id,
            "query": data.query,
            "source": data.source,
            "created_at": datetime_to_timestamp(data.created_at),
        }


class HitReq(FlaskForm):
    """知识库召回测试请求"""
    query = StringField("query", validators=[
        DataRequired("查询语句不能为空"),
        Length(max=200, message="查询语句的最大长度不能超过200")
    ])
    retrieval_strategy = StringField("retrieval_strategy", validators=[
        DataRequired("检索策略不能为空"),
        AnyOf([item.value for item in RetrievalStrategy], message="检索策略格式错误")
    ])
    k = IntegerField("k", validators=[
        DataRequired("最大召回数量不能为空"),
        NumberRange(min=0, max=10, message="最大召回数量的范围在1-10")
    ])
    score = FloatField("score", validators=[
        NumberRange(min=0, max=0.99, message="最小匹配度范围在0-0.99")
    ])
