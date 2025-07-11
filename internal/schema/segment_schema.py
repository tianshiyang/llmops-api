#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.7.25 PM4:51
@Author  : tianshiyang
@File    : segment_schema.py
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms.fields.simple import StringField
from wtforms.validators import Optional, DataRequired, ValidationError

from internal.exception import ValidateErrorException
from internal.lib.helper import datetime_to_timestamp
from internal.model.dataset import Segment
from internal.schema import ListField
from pkg.paginator.paginator import PaginatorReq


class GetSegmentsWithPageReq(PaginatorReq):
    """获取文档片段列表请求"""
    search_word = StringField("search_word", default="", validators=[
        Optional()
    ])


class GetSegmentsWithPageResp(Schema):
    """获取文档片段列表响应结构"""
    id = fields.UUID(dump_default="")
    document_id = fields.UUID(dump_default="")
    dataset_id = fields.UUID(dump_default="")
    position = fields.Integer(dump_default=0)
    content = fields.String(dump_default="")
    keywords = fields.List(fields.String, dump_default=[])
    character_count = fields.Integer(dump_default=0)
    token_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
    enabled = fields.Boolean(dump_default=False)
    disabled_at = fields.Integer(dump_default=0)
    status = fields.String(dump_default="")
    error = fields.String(dump_default="")
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Segment, **kwargs):
        return {
            "id": data.id,
            "document_id": data.document_id,
            "dataset_id": data.dataset_id,
            "position": data.position,
            "content": data.content,
            "keywords": data.keywords,
            "character_count": data.character_count,
            "token_count": data.token_count,
            "hit_count": data.hit_count,
            "enabled": data.enabled,
            "disabled_at": datetime_to_timestamp(data.disabled_at),
            "status": data.status,
            "error": data.error,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }


class CreateSegmentReq(FlaskForm):
    """创建文档片段请求结构"""
    content = StringField("content", validators=[
        DataRequired("片段内容不能为空")
    ])
    keywords = ListField("keywords")

    def validate_keywords(self, field: ListField):
        """校验关键词列表"""
        if field.data is None:
            field.data = []
        if not isinstance(field.data, list):
            raise ValidationError("关键词列表格式必须是数组")

        # 校验数据长度，最长不能超过10个关键词
        if len(field.data) > 10:
            raise ValidationError("关键词必须是字符串")

        # 3. 循环关键词信息，关键词必须是字符串
        for keyword in field.data:
            if not isinstance(keyword, str):
                raise ValidationError("关键词必须是字符串")

        # 4.删除重复数据并更新
        field.data = list(dict.fromkeys(field.data))


class GetSegmentResp(Schema):
    """获取文档详情响应结构"""
    id = fields.UUID(dump_default="")
    document_id = fields.UUID(dump_default="")
    dataset_id = fields.UUID(dump_default="")
    position = fields.Integer(dump_default=0)
    content = fields.String(dump_default="")
    keywords = fields.List(fields.String, dump_default=[])
    character_count = fields.Integer(dump_default=0)
    token_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
    hash = fields.String(dump_default="")
    enabled = fields.Boolean(dump_default=False)
    disabled_at = fields.Integer(dump_default=0)
    status = fields.String(dump_default="")
    error = fields.String(dump_default="")
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Segment, **kwargs):
        return {
            "id": data.id,
            "document_id": data.document_id,
            "dataset_id": data.dataset_id,
            "position": data.position,
            "content": data.content,
            "keywords": data.keywords,
            "character_count": data.character_count,
            "token_count": data.token_count,
            "hit_count": data.hit_count,
            "hash": data.hash,
            "enabled": data.enabled,
            "disabled_at": datetime_to_timestamp(data.disabled_at),
            "status": data.status,
            "error": data.error,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }
