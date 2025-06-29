#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/17 23:02
@Author  : 1685821150@qq.com
@File    : config.py
"""
import os
from typing import Any

from .default_config import DEFAULT_CONFIG


def _get_env(key: str) -> Any:
    """从环境变量中获取配置项，如果找不到则返回默认值"""
    return os.getenv(key, default=DEFAULT_CONFIG.get(key))


def _get_bool_env(key: str):
    value: str = _get_env(key)
    return value.lower() == "true" if value is not None else False


class Config:
    def __init__(self):
        # 关闭wtf的csrf保护
        self.WTF_CSRF_ENABLED = _get_bool_env("WTF_CSRF_ENABLED")

        # 配置数据库设置
        self.SQLALCHEMY_DATABASE_URI = _get_env("SQLALCHEMY_DATABASE_URI")
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(_get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(_get_env("SQLALCHEMY_POOL_RECYCLE")),
        }
        self.SQLALCHEMY_ECHO = _get_bool_env("SQLALCHEMY_ECHO")

        # Redis配置
        self.REDIS_HOST = _get_env("REDIS_HOST")
        self.REDIS_PORT = _get_env("REDIS_PORT")
        self.REDIS_USERNAME = _get_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = _get_env("REDIS_PASSWORD")
        self.REDIS_DB = _get_env("REDIS_DB")
        self.REDIS_USE_SSL = _get_bool_env("REDIS_USE_SSL")
