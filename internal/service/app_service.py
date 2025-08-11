#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 17:37
@Author  : 1685821150@qq.com
@File    : app_service.py
"""
from uuid import UUID
from dataclasses import dataclass

from injector import inject

from internal.entity.app_entity import AppStatus, AppConfigType, DEFAULT_APP_CONFIG
from internal.exception import NotFoundException, ForbiddenException
from internal.model import App, Account, AppConfigVersion
from internal.schema.app_schema import CreateAppReq
from internal.service.base_service import BaseService

from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AppService(BaseService):
    """应用服务逻辑"""

    db: SQLAlchemy

    def create_app(self, req: CreateAppReq, account: Account) -> App:
        """创建Agent应用服务"""
        # 1. 开启数据库自动提交上下文
        with self.db.auto_commit():
            # 2. 创建应用记录，并刷新数据，从而可以拿到应用id
            app = App(
                account_id=account.id,
                name=req.name.data,
                icon=req.icon.data,
                description=req.description.data,
                status=AppStatus.DRAFT.value
            )
            self.db.session.add(app)
            self.db.session.flush()
            self.db.session.refresh(app)

            # 3. 添加草稿记录
            app_config_version = AppConfigVersion(
                app_id=app.id,
                version=0,
                config_type=AppConfigType.DRAFT.value,
                **DEFAULT_APP_CONFIG,
            )
            self.db.session.add(app_config_version)
            self.db.session.flush()
            self.db.session.refresh(app_config_version)

            # 4.为应用添加草稿配置id
            app.draft_app_config_id = app_config_version.id

        # 5.返回创建的应用记录
        return app

    def get_app(self, app_id: UUID, account: Account) -> App:
        """根据传递的id获取应用的基础信息"""
        # 1.查询数据库获取应用基础信息
        app = self.get(App, app_id)

        # 2.判断应用是否存在
        if not app:
            raise NotFoundException("该应用不存在，请核实后重试")

        # 3.判断当前账号是否有权限访问该应用
        if app.account_id != account.id:
            raise ForbiddenException("当前账号无权限访问该应用，请核实后尝试")

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
