#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 17.4.25 PM10:31
@Author  : 1685821150@qq.com
@File    : app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class CompletionReq(FlaskForm):
    query = StringField("query", validators=[
        DataRequired(message="用户的提问是必填"),
        Length(max=2000, message="用户的提问最大长度是2000")
    ])
