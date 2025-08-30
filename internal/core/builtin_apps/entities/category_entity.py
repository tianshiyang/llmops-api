#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 30.8.25 PM11:39
@Author  : tianshiyang
@File    : categories.py
"""
from pydantic import BaseModel, Field


class CategoryEntity(BaseModel):
    """内置工具分类实体"""
    category: str = Field(default="")  # 分类唯一标识
    name: str = Field(default="")  # 分类对应的名称
