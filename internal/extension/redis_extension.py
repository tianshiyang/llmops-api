#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.6.25 PM10:44
@Author  : tianshiyang
@File    : redis_extension.py
"""
import redis
from flask import Flask
from redis.connection import Connection, SSLConnection

# redis客户端
redis_client = redis.Redis()


def init_app(app: Flask):
    client_class = Connection
    if app.config.get("REDIS_USE_SSL", False):
        client_class = SSLConnection

    # 2.创建redis连接池
    redis.ConnectionPool(**{
        "host": app.config.get("REDIS_HOST", "localhost"),
        "port": app.config.get("REDIS_PORT", 6379),
        "username": app.config.get("REDIS_USERNAME", None),
        "password": app.config.get("REDIS_PASSWORD", None),
        "db": app.config.get("REDIS_DB", 0),
        "encoding": "utf-8",
        "encoding_errors": "strict",
        "decode_responses": False
    }, client_class=client_class)

    app.extensions['redis'] = redis_client
