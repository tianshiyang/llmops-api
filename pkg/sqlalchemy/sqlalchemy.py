#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 22:08
@Author  : 1685821150@qq.com
@File    : sqlalchemy.py
"""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQAlchemy


class SQLAlchemy(_SQAlchemy):
    """重写Flask-SQLAlchemy中的核心类，实现自动提交"""

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
