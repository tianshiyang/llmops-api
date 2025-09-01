#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 1.9.25 PM11:34
@Author  : tianshiyang
@File    : workflow_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Regexp, URL

from internal.core.workflow.entities.workflow_entity import WORKFLOW_CONFIG_NAME_PATTERN


class CreateWorkflowReq(FlaskForm):
    name = StringField("name", validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    tool_call_name = StringField("tool_call_name", validators=[
        DataRequired("英文名称不能为空"),
        Length(max=50, message="英文名称不能超过50个字符"),
        Regexp(WORKFLOW_CONFIG_NAME_PATTERN, message="英文名称仅支持字母、数字和下划线，且以字母/下划线为开头")
    ])
    icon = StringField("icon", validators=[
        DataRequired("工作流图标不能为空"),
        URL(message="工作流图标必须是图片URL地址"),
    ])
    description = StringField("description", validators=[
        DataRequired("工作流描述不能为空"),
        Length(max=1024, message="工作流描述不能超过1024个字符")
    ])
