#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:13
@Author  : tianshiyang
@File    : dataset_schema.py
"""
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length, URL, Optional


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
