#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.8.25 PM4:54
@Author  : tianshiyang
@File    : api_key_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import Length


class CreateApiKeyReq(FlaskForm):
    """创建API秘钥请求"""
    is_active = BooleanField("is_active")
    remark = StringField("remark", validators=[
        Length(max=100, message="秘钥备注不能超过100个字符")
    ])
