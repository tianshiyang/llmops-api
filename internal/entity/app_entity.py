#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.8.25 PM5:36
@Author  : tianshiyang
@File    : app_entity.py
"""
from enum import Enum


class AppConfigType(Enum):
    """应用配置类型枚举类"""
    DRAFT = "draft"
    PUBLISHED = "published"
