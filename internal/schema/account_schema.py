#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 8.8.25 AM11:28
@Author  : tianshiyang
@File    : account_schema.py
"""
from marshmallow import Schema, fields, pre_dump

from internal.lib.helper import datetime_to_timestamp
from internal.model import Account


class GetCurrentUserResp(Schema):
    """获取当前登录账号信息响应"""
    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    email = fields.String(dump_default="")
    avatar = fields.String(dump_default="")
    last_login_at = fields.Integer(dump_default=0)
    last_login_ip = fields.String(dump_default="")
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Account, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "email": data.email,
            "avatar": data.avatar,
            "last_login_at": datetime_to_timestamp(data.last_login_at),
            "last_login_ip": data.last_login_ip,
            "created_at": datetime_to_timestamp(data.created_at),
        }
