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

    # Redis数据库配置
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_USERNAME": "",
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    "REDIS_USE_SSL": "False",
}
