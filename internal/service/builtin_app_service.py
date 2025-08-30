#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 30.8.25 PM11:33
@Author  : tianshiyang
@File    : builtin_app_service.py
"""
from internal.core.builtin_apps.builtin_app_manager import BuiltinAppManager
from internal.core.builtin_apps.entities.builtin_app_entity import BuiltinAppEntity
from internal.core.builtin_apps.entities.category_entity import CategoryEntity
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from injector import inject
from dataclasses import dataclass


@inject
@dataclass
class BuiltinAppService(BaseService):
    """内置应用服务"""
    db: SQLAlchemy
    builtin_app_manager: BuiltinAppManager

    def get_categories(self) -> list[CategoryEntity]:
        """获取分类列表信息"""
        return self.builtin_app_manager.get_categories()

    def get_builtin_apps(self) -> list[BuiltinAppEntity]:
        """获取所有内置应用实体信息列表"""
        return self.builtin_app_manager.get_builtin_apps()
