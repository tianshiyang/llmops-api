#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.9.25 PM9:25
@Author  : tianshiyang
@File    : assistant_agent_schema.py
"""
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


class AssistantAgentChat(FlaskForm):
    query = StringField("query", validators=[
        DataRequired(message="用户提问query不能为空")
    ])
