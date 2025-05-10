#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/17 23:05
@Author  : 1685821150@qq.com
@File    : default_config.py
"""
DEFAULT_CONFIG = {
    # wft配置
    "WTF_CSRF_ENABLED": "False",

    # SQLAlchemy数据库配置
    "SQLALCHEMY_DATABASE_URI": "",
    "SQLALCHEMY_POOL_SIZE": 30,
    "SQLALCHEMY_POOL_RECYCLE": 3600,
    "SQLALCHEMY_ECHO": "True",
}
