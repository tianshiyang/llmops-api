#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 16:59
@Author  : 1685821150@qq.com
@File    : moudle.py
"""
from pkg.sqlalchemy import SQLAlchemy
from injector import Module, Binder
from flask_migrate import Migrate
from internal.extension.migrate_extension import migrate

from internal.extension.database_extension import db


class ExtensionModule(Module):
    """扩展模块的依赖注入"""

    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
