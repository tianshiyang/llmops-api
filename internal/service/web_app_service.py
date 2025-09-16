#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.9.25 PM9:51
@Author  : tianshiyang
@File    : web_app_service.py
"""
from internal.entity.app_entity import AppStatus
from internal.exception import NotFoundException
from internal.model import App
from internal.service.base_service import BaseService
from dataclasses import dataclass
from injector import inject

from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class WebAppService(BaseService):
    db: SQLAlchemy

    def get_web_app(self, token: str) -> App:
        """根据传递的token获取WebApp实例"""
        app = self.db.session.query(App).filter(
            App.token == token
        ).one_or_none()
        if not app or app.status != AppStatus.PUBLISHED:
            raise NotFoundException("该WebApp不存在或者未发布，请核实后重试")

        # 2.返回查询的应用
        return app
