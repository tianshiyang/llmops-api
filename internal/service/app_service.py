#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 17:37
@Author  : 1685821150@qq.com
@File    : app_service.py
"""
import uuid
from dataclasses import dataclass

from injector import inject

from internal.model import App

from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AppService:
    """应用服务逻辑"""

    db: SQLAlchemy

    def create_app(self):
        with self.db.auto_commit():
            # 1. 创建模型实体类
            app = App(name="测试机器人", account_id=uuid.uuid4(), icon="", description="这是一个简单的聊天机器人")
            # 2. 将模型添加到实体类中
            self.db.session.add(app)
            # 3. 提交session会话
            self.db.session.commit()
        return app

    def get_app(self, id: uuid.UUID) -> App:
        app = self.db.session.query(App).get(id)
        return app

    def update_app(self, id):
        with self.db.auto_commit():
            app = self.db.session.query(App).get(id)
            app.name = '慕课聊天机器人'
            self.db.session.commit()
        return app

    def delete_app(self, id):
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
            self.db.session.commit()
        return app
